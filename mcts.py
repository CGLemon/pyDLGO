# -*- coding: utf-8 -*-

from config import INPUT_CHANNELS
from board import Board, PASS, RESIGN, BLACK, WHITE
from network import Network
from time_control import TimeControl

import math

class Node:
    CPUCT = 0.5
    def __init__(self, p):
        self.policy = p  # The network raw policy from its parents node.
        self.nn_eval = 0 # The network raw eval from this node.

        self.values = 0 # The accumulate winrate.
        self.visits = 0 # The accumulate node visits.
                        # The Q value must be equal to (self.values / self.visits)
        self.children = {}

    def clamp(self, v):
        # Map the winrate 1 ~ -1 to 1 ~ 0.
        return (v + 1) / 2

    def inverse(self, v):
        # swap side to move winrate. 
        return 1 - v;

    def expand_children(self, board: Board, network: Network):
        policy, value = network.get_outputs(board.get_features())
        for idx in range(board.num_intersections):
            vtx = board.index_to_vertex(idx)

            # Remove the illegal move.
            if board.legal(vtx):
                p = policy[idx]
                self.children[vtx] = Node(p)

        # The pass move is alwaly the legal move. We don't need to
        # check it.
        self.children[PASS] = Node(policy[board.num_intersections])
        self.nn_eval = self.clamp(value[0])

        return self.nn_eval

    def remove_superko(self, board: Board):
        remove_list = []
        for vtx, child in self.children.items():
            next_board = board.copy()
            next_board.play(vtx)
            if next_board.superko():
                remove_list.append(vtx)
        for vtx in remove_list:
            self.children.pop(vtx)

    def puct_select(self):
        parent_visits = 1 # We set the initialization value is 1 because we want to get the 
                          # best policy value in the first selection.
        for _, child in self.children.items():
            parent_visits += child.visits

        numerator = math.sqrt(parent_visits)

        puct_list = []
        for vtx, child in self.children.items():
            q_value = self.clamp(0) # fair winrate if the node is no visit.
            if child.visits is not 0:
                q_value = self.inverse(child.values / child.visits)
            puct = q_value + self.CPUCT * child.policy * (numerator / (1+child.visits))
            puct_list.append((puct, vtx))
        return max(puct_list)[1]

    def update(self, v):
        self.values += v
        self.visits += 1

    def get_best_move(self, resign_threshold):
        gather_list = []
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))

        vtx = max(gather_list)[1]
        child = self.children[vtx]
        if self.inverse(child.values / child.visits) < resign_threshold:
            return RESIGN
        return vtx

    def to_string(self, board: Board):
        out = str()
        out += "Root -> W: {:.2f}%, P: {:.2f}%, V: {}\n".format(
                    self.values/self.visits,
                    self.policy,
                    self.visits)

        gather_list = []
        for vtx, child in self.children.items():
            gather_list.append((child.visits, vtx))
        gather_list.sort(reverse=True)

        for _, vtx in  gather_list:
            child = self.children[vtx]
            if child.visits is not 0:
                out += "  {:4} -> W: {:.2f}%, P: {:.2f}%, V: {}\n".format(
                           board.vertex_to_text(vtx),
                           self.inverse(child.values/child.visits),
                           child.policy,
                           child.visits)
        return out

class Search:
    def __init__(self, board: Board, network: Network, time_control: TimeControl):
        self.root_board = board
        self.root_node = None
        self.network = network
        self.time_control = time_control

    def prepare_root_node(self):
        # Expand the root node first.
        self.root_node = Node(1)
        val = self.root_node.expand_children(self.root_board, self.network)

        # In order to avoid overhead, we only remove the superko position in
        # the root.
        self.root_node.remove_superko(self.root_board)
        self.root_node.update(val)

    def play_simulation(self, color, curr_board, node):
        value = None
        if curr_board.num_passes >= 2:
            # The game is over.
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
        elif len(node.children) is not 0:
            # Select the next node by PUCT algorithm. 
            vtx = node.puct_select()
            curr_board.to_move = color
            curr_board.play(vtx)
            color = (color + 1) % 2
            next_node = node.children[vtx]

            # Search the next node.
            value = self.play_simulation(color, curr_board, next_node)
        else:
            # This is the termainated node. Now to expand it. 
            value = node.expand_children(curr_board, self.network)

        assert value is not None, ""
        node.update(value)

        return node.inverse(value)

    def think(self, playouts, resign_threshold, verbose):
        if self.root_board.num_passes >= 2:
            return PASS

        self.time_control.clock()
        if verbose:
            print(self.time_control)

        to_move = self.root_board.to_move
        bsize = self.root_board.board_size
        move_num = self.root_board.move_num
        max_time = self.time_control.get_thinking_time(to_move, bsize, move_num)

        self.prepare_root_node()
        for _ in range(playouts):
            if self.time_control.should_stop(max_time):
                break

            # The main body of Monte carlo tree search.
            curr_board = self.root_board.copy()
            color = curr_board.to_move
            self.play_simulation(color, curr_board, self.root_node)

        self.time_control.took_time(to_move)
        if verbose:
            print(self.root_node.to_string(self.root_board))
            print(self.time_control)
        return self.root_node.get_best_move(resign_threshold)
