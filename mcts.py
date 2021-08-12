from config import INPUT_CHANNELS
from board import Board, PASS
from network import Network

import torch

INVALID_TURN = 0
MY_TURN = 1
OPP_TURN = 2

class Node:
    CPUCT = 1.2
    def __init__(self, p)
        self.policy = p
        self.nn_eval = 0

        self.values = 0
        self.visits = 0
        self.turn = INVALID_TURN
        self.children = {}

    def expend_children(self, board: Board, network: Network):
        policy, eval = network(board.get_features())
        for idx in range(board.num_intersections):
            p = policy[0, idx]
            vtx = board.index_to_vertex(idx)
            if board.legal(vtx):
                self.children[vtx] = Node(p)
        self.children[PASS] = Node(policy[0, board.num_intersections])
        self.nn_eval = eval[0, 0]

def Search:
    def __init__(self, board: Board, network: Network):
        self.root_board = board
        self.network = network
