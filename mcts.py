# -*- coding: utf-8 -*-

from config import INPUT_CHANNELS
from board import Board, PASS, BLACK, WHITE
from network import Network

import math

class Node:
    CPUCT = 0.5
    def __init__(self, p):
        self.policy = p
        self.nn_eval = 0

        self.values = 0
        self.visits = 0
        self.children = {}

    def clamp(self, v):
        # map the winrate 1 ~ -1 to 1 ~ 0
        return (v + 1) / 2

    def expend_children(self, board: Board, network: Network):
        policy, value = network.get_outputs(board.get_features())
        for idx in range(board.num_intersections):
            p = policy[idx]
            vtx = board.index_to_vertex(idx)
            if board.legal(vtx):
                self.children[vtx] = Node(p)
        self.children[PASS] = Node(policy[board.num_intersections]) # pass
        self.nn_eval = self.clamp(value[0])
        return self.nn_eval

    def uct_select(self):
        parent_visits = 1
        for _, child in  self.children.items():
            parent_visits += child.visits

        numerator = math.sqrt(parent_visits)

        puct_list = []
        for vtx, child in  self.children.items():
            q_value = self.clamp(0)
            if child.visits is not 0:
                q_value = self.clamp(-child.values / child.visits)
            puct = q_value + self.CPUCT * child.policy * (numerator / (1+child.visits))
            puct_list.append((puct, vtx))
        return max(puct_list)[1]

    def update(self, v):
        self.values += v
        self.visits += 1

    def get_best_move(self):
        gather_list = []
        for vtx, child in  self.children.items():
            gather_list.append((child.visits, vtx))
        return max(gather_list)[1]

    def dump(self, board: Board):
        out = str()
        out += "Root -> W: {:.2f}%, P: {:.2f}%, V: {}\n".format(
                    self.values,
                    self.policy,
                    self.visits)
        for vtx, child in  self.children.items():
            if child.visits is not 0:
                out += "  {:4} -> W: {:.2f}%, P: {:.2f}%, V: {}\n".format(
                           board.vertex_to_text(vtx),
                           child.values,
                           child.policy,
                           child.visits)
        print(out)

class Search:
    def __init__(self, board: Board, network: Network):
        self.root_board = board
        self.root_node = None
        self.network = network

    def prepare_root_node(self):
        self.root_node = Node(1)
        val = self.root_node.expend_children(self.root_board, self.network)
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
            # Expending...
            vtx = node.uct_select()
            curr_board.to_move = color
            curr_board.play(vtx)
            color = (color + 1) % 2
            next_node = node.children[vtx]
            value = self.play_simulation(color, curr_board, next_node)
        else:
            value = node.expend_children(curr_board, self.network)

        assert value is not None, ""
        node.update(value)

        return value

    def think(self, playouts, verbose):
        self.prepare_root_node()
        for _ in range(playouts):
            curr_board = self.root_board.copy()
            color = curr_board.to_move
            self.play_simulation(color, curr_board, self.root_node)
        if verbose:
            self.root_node.dump(self.root_board)
        return self.root_node.get_best_move()
