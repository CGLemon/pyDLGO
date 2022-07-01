from config import INPUT_CHANNELS
from board import Board, PASS, RESIGN, BLACK, WHITE
from network import Network
from time_control import TimeControl

from sys import stderr
import math

class Node:
    # TODO: Tnue C_PUCT parameter.
    C_PUCT = 0.5 # The PUCT hyperparameter.
    def __init__(self, p):
        self.policy = p  # The network raw policy from its parents node.
        self.nn_eval = 0 # The network raw eval from this node.

        self.values = 0 # The accumulate winrate.
        self.visits = 0 # The accumulate node visits.
                        # The Q value must be equal to (self.values / self.visits)
        self.children = {} # Next node.

    def clamp(self, v):
        # Map the winrate 1 ~ -1 to 1 ~ 0.
        return (v + 1) / 2

    def inverse(self, v):
        # Swap the side to move winrate. 
        return 1 - v;

    def expand_children(self, board: Board, network: Network):
        if board.last_move == PASS:
            score = board.final_score()
            if (board.to_move == BLACK and score > 0) or \
                    (board.to_move == WHITE and score < 0):
                # Play pass move if we win the game.
                self.children[PASS] = Node(1.0)
                return 1;

        # Compute the net results.
        policy, value = network.get_outputs(board.get_features())

        for idx in range(board.num_intersections):
            vtx = board.index_to_vertex(idx)

            # Remove the all illegal move.
            if board.legal(vtx):
                p = policy[idx]
                self.children[vtx] = Node(p)

        # The pass move is alwaly the legal move. We don't need to
        # check it.
        self.children[PASS] = Node(policy[board.num_intersections])
        self.nn_eval = self.clamp(value[0])

        return self.nn_eval

    def remove_superko(self, board: Board):
        # Remove all superko moves.

        remove_list = []
        for vtx, _ in self.children.items():
            if vtx != PASS:
                next_board = board.copy()
                next_board.play(vtx)
                if next_board.superko():
                    remove_list.append(vtx)
        for vtx in remove_list:
            self.children.pop(vtx)

    def puct_select(self):
        parent_visits = max(self.visits, 1) # The parent visits must great than 1 because we want to get the
                                            # best policy value if it is the first selection.
        numerator = math.sqrt(parent_visits)

        puct_list = []

        # Select the best node by PUCT algorithm. 
        for vtx, child in self.children.items():
            q_value = self.clamp(0) # Fair winrate if the node is no visit.
            if child.visits != 0:
                q_value = self.inverse(child.values / child.visits)
            puct = q_value + self.C_PUCT * child.policy * (numerator / (1+child.visits))
            puct_list.append((puct, vtx))
        return max(puct_list)[1]

    def update(self, v):
        self.values += v
        self.visits += 1

    def get_best_prob_move(self):
        gather_list = []
        for vtx, child in self.children.items():
            gather_list.append((child.policy, vtx))
        return max(gather_list)[1]

    def get_best_move(self, resign_threshold):
        # Return best probability move if there are no playouts.
        if self.visits == 1:
            if self.values < resign_threshold:
                return 0;
            else:
                return self.get_best_prob_move()

        # Get best move by number of node visits.
        gather_list = []
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))

        vtx = max(gather_list)[1]
        child = self.children[vtx]

        # Play resin move if we think we have already lost.
        if self.inverse(child.values / child.visits) < resign_threshold:
            return RESIGN

        return vtx

    def to_string(self, board: Board):
        # Collect some node information in order to debug.

        out = str()
        out += "Root -> W: {:5.2f}%, V: {}\n".format(
                    100.0 * self.values/self.visits,
                    self.visits)

        gather_list = []
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))
        gather_list.sort(reverse=True)

        for _, vtx in gather_list:
            child = self.children[vtx]
            if child.visits != 0:
                out += "  {:4} -> W: {:5.2f}%, P: {:5.2f}%, V: {}\n".format(
                           board.vertex_to_text(vtx),
                           100.0 * self.inverse(child.values/child.visits),
                           100.0 * child.policy,
                           child.visits)
        return out

#TODO: The MCTS performance is bad. Maybe the recursive is much
#      slower than loop. Or self.children do too many times mapping
#      operator. Try to fix it.
class Search:
    def __init__(self, board: Board, network: Network, time_control: TimeControl):
        self.root_board = board # Root board positions, all simulation boards will fork from it.
        self.root_node = None # Root node, start the PUCT search from it.
        self.network = network
        self.time_control = time_control

    def _prepare_root_node(self):
        # Expand the root node first.
        self.root_node = Node(1)
        val = self.root_node.expand_children(self.root_board, self.network)

        # In order to avoid overhead, we only remove the superko position in
        # the root.
        self.root_node.remove_superko(self.root_board)
        self.root_node.update(val)

    def _descend(self, color, curr_board, node):
        value = None
        if curr_board.num_passes >= 2:
            # The game is over. Compute the final score.
            score = curr_board.final_score()
            if score > 1e-4:
                # The black player is winner.
                value = 1 if color is BLACK else 0
            elif score < -1e-4:
                # The white player is winner.
                value = 1 if color is WHITE else 0
            else:
                # The game is draw
                value = 0.5
        elif len(node.children) != 0:
            # Select the next node by PUCT algorithm. 
            vtx = node.puct_select()
            curr_board.to_move = color
            curr_board.play(vtx)
            color = (color + 1) % 2
            next_node = node.children[vtx]

            # go to the next node.
            value = self._descend(color, curr_board, next_node)
        else:
            # This is the termainated node. Now try to expand it. 
            value = node.expand_children(curr_board, self.network)

        assert value != None, ""
        node.update(value)

        return node.inverse(value)

    def think(self, playouts, resign_threshold, verbose):
        # Get the best move with Monte carlo tree. The time controller and max playouts limit
        # the search. More thinking time or playouts is stronger.

        if self.root_board.num_passes >= 2:
            return PASS

        self.time_control.clock()
        if verbose:
            stderr.write(str(self.time_control))
            stderr.write("\n")
            stderr.flush()

        # Prepare some basic information.
        to_move = self.root_board.to_move
        bsize = self.root_board.board_size
        move_num = self.root_board.move_num

        # Compute thinking time limit.
        max_time = self.time_control.get_thinking_time(to_move, bsize, move_num)

        # Try to expand the root node first.
        self._prepare_root_node()

        for _ in range(playouts):
            if self.time_control.should_stop(max_time):
                break

            # Copy the root board because we need to simulate the current board.
            curr_board = self.root_board.copy()
            color = curr_board.to_move

            # Start the Monte Carlo tree search.
            self._descend(color, curr_board, self.root_node)

        # Eat the remaining time. 
        self.time_control.took_time(to_move)

        if verbose:
            # Dump verbose to stderr because we want to debug it on GTP
            # interface(sabaki).
            stderr.write(self.root_node.to_string(self.root_board))
            stderr.write(str(self.time_control))
            stderr.write("\n")
            stderr.flush()

        out_verbose = self.root_node.to_string(self.root_board)

        return self.root_node.get_best_move(resign_threshold), out_verbose
