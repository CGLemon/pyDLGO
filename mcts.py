from board import Board, PASS, RESIGN, BLACK, WHITE
from network import Network
from time_control import TimeControl

from sys import stderr, stdout, stdin
import math
import time
import select

class Node:
    C_PUCT = 0.5 # The PUCT hyperparameter. This value should be 1.25 in
                 # AlphaGo Zero. However our value range is 1 ~ 0, not 1 ~ -1.
                 # So we rescale this value as 0.5 (LeelaZero use it).
    def __init__(self, p):
        self.policy = p  # The network raw policy from its parents node.
        self.nn_eval = 0 # The network raw eval from this node.

        self.values = 0 # The accumulation winrate.
        self.visits = 0 # The accumulation node visits.
                        # The Q value must be equal to (self.values / self.visits)
        self.children = dict() # Next node.

    def clamp(self, v):
        # Map the winrate 1 ~ -1 to 1 ~ 0.
        return (v + 1) / 2

    def inverse(self, v):
        # Swap the side to move winrate. 
        return 1 - v

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

        # The nn eval is side-to-move winrate. 
        self.nn_eval = self.clamp(value[0])

        return self.nn_eval

    def remove_superko(self, board: Board):
        # Remove all superko moves.

        remove_list = list()
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
        puct_list = list()

        # Select the best node by PUCT algorithm. 
        for vtx, child in self.children.items():
            q_value = 0 # init to lose

            if child.visits != 0:
                q_value = self.inverse(child.values / child.visits)

            puct = q_value + self.C_PUCT * child.policy * (numerator / (1+child.visits))
            puct_list.append((puct, vtx))
        return max(puct_list)[1]

    def update(self, v):
        self.values += v
        self.visits += 1

    def get_best_prob_move(self):
        gather_list = list()
        for vtx, child in self.children.items():
            gather_list.append((child.policy, vtx))
        return max(gather_list)[1]

    def get_best_move(self, resign_threshold):
        # Return best probability move if there are no playouts.
        if self.visits == 1:
            if resign_threshold is not None and \
                   self.values < resign_threshold:
                return RESIGN
            else:
                return self.get_best_prob_move()

        # Get best move by number of node visits.
        gather_list = list()
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))

        vtx = max(gather_list)[1]
        child = self.children[vtx]

        # Play resin move if we think we have already lost.
        if resign_threshold is not None and \
               self.inverse(child.values / child.visits) < resign_threshold:
            return RESIGN
        return vtx

    def to_string(self, board: Board):
        # Collect some node information in order to debug.

        out = str()
        out += "Root -> W: {:5.2f}%, V: {}\n".format(
                    100.0 * self.values/self.visits,
                    self.visits)

        gather_list = list()
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

    def get_pv(self, board: Board, pv_str):
        # Get the best Principal Variation list since this
        # node.
        if len(self.children) == 0: 
            return pv_str

        next_vtx = self.get_best_move(None)
        next = self.children[next_vtx]
        pv_str += "{} ".format(board.vertex_to_text(next_vtx))
        return next.get_pv(board, pv_str)

    def to_lz_analysis(self, board: Board):
        # Output the leela zero analysis string. Watch the detail
        # here: https://github.com/SabakiHQ/Sabaki/blob/master/docs/guides/engine-analysis-integration.md
        out = str()

        gather_list = list()
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))
        gather_list.sort(reverse=True)

        if len(gather_list) == 0:
            return str()

        i = 0
        for _, vtx in gather_list:
            child = self.children[vtx]
            if child.visits != 0:
                winrate = self.inverse(child.values/child.visits)
                prior = child.policy
                lcb = winrate
                order = i
                pv = "{} ".format(board.vertex_to_text(vtx))
                out += "info move {} visits {} winrate {} prior {} lcb {} order {} pv {}".format(
                           board.vertex_to_text(vtx),
                           child.visits,
                           round(10000 * winrate),
                           round(10000 * prior),
                           round(10000 * lcb),
                           order,
                           child.get_pv(board, pv))
                i+=1
        out += '\n'
        return out



# TODO: The MCTS performance is bad. Maybe the recursive is much
#       slower than loop. Or self.children do too many times mapping
#       operator. Try to fix it.
class Search:
    def __init__(self, board: Board, network: Network, time_control: TimeControl):
        self.root_board = board # Root board positions, all simulation boards will fork from it.
        self.root_node = None # Root node, start the PUCT search from it.
        self.network = network
        self.time_control = time_control
        self.analysis_tag = {
            "interval" : -1
        }

    def _prepare_root_node(self):
        # Expand the root node first.
        self.root_node = Node(1)
        val = self.root_node.expand_children(self.root_board, self.network)

        # In order to avoid overhead, we only remove the superko positions in
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

    def ponder(self, playouts, verbose):
        if self.root_board.num_passes >= 2:
            return str()

        analysis_clock = time.time()
        interval = self.analysis_tag["interval"]

        # Try to expand the root node first.
        self._prepare_root_node()

        for p in range(playouts):
            if p != 0 and \
                   interval > 0 and \
                   time.time() - analysis_clock > interval:
                analysis_clock = time.time()
                stdout.write(self.root_node.to_lz_analysis(self.root_board))
                stdout.flush()

            rlist, _, _ = select.select([stdin], [], [], 0)
            if rlist:
                break

            # Copy the root board because we need to simulate the current board.
            curr_board = self.root_board.copy()
            color = curr_board.to_move

            # Start the Monte Carlo tree search.
            self._descend(color, curr_board, self.root_node)

        # Always dump last tree stats for GUI, like Sabaki.
        if self.root_node.visits > 1:
            stdout.write(self.root_node.to_lz_analysis(self.root_board))
            stdout.flush()

        out_verbose = self.root_node.to_string(self.root_board)
        if verbose:
            # Dump verbose to stderr because we want to debug it on GTP
            # interface(sabaki).
            stderr.write(out_verbose)
            stderr.write("\n")
            stderr.flush()

        return out_verbose

    def think(self, playouts, resign_threshold, verbose):
        # Get the best move with Monte carlo tree. The time controller and max playouts limit
        # the search. More thinking time or playouts is stronger.

        if self.root_board.num_passes >= 2:
            return PASS, str()

        analysis_clock = time.time()
        interval = self.analysis_tag["interval"]
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

        for p in range(playouts):
            if p != 0 and \
                   interval > 0 and \
                   time.time() - analysis_clock > interval:
                analysis_clock = time.time()
                stdout.write(self.root_node.to_lz_analysis(self.root_board))
                stdout.flush()

            if self.time_control.should_stop(max_time):
                break

            # Copy the root board because we need to simulate the current board.
            curr_board = self.root_board.copy()
            color = curr_board.to_move

            # Start the Monte Carlo tree search.
            self._descend(color, curr_board, self.root_node)

        # Eat the remaining time.
        self.time_control.took_time(to_move)

        # Always dump last tree stats for GUI, like Sabaki.
        if self.root_node.visits > 1:
            stdout.write(self.root_node.to_lz_analysis(self.root_board))
            stdout.flush()

        out_verbose = self.root_node.to_string(self.root_board)
        if verbose:
            # Dump verbose to stderr because we want to debug it on GTP
            # interface(sabaki).
            stderr.write(out_verbose)
            stderr.write(str(self.time_control))
            stderr.write("\n")
            stderr.flush()

        return self.root_node.get_best_move(resign_threshold), out_verbose
