# -*- coding: utf-8 -*-

from config import BOARD_SIZE, KOMI, INPUT_CHANNELS, PAST_MOVES
import numpy as np
import copy

BLACK = 0
WHITE = 1
EMPTY = 2
INVLD = 3
X_LABELS = "ABCDEFGHJKLMNOPQRST"

NUM_VERTICES = (BOARD_SIZE+2) ** 2
NUM_INTESECTIONS = BOARD_SIZE ** 2

PASS = -1  # pass
RESIGN = -2 # resign
NULL_VERTEX = NUM_VERTICES+1 # invalid position

class StoneGroup(object):
    def __init__(self):
        self.lib_cnt = NULL_VERTEX  # liberty count
        self.size = NULL_VERTEX  # stone size
        self.v_atr = NULL_VERTEX  # liberty position if in Atari
        self.libs = set()  # set of liberty positions

    def clear(self, stone=True):
        # clear as placed stone or empty
        self.lib_cnt = 0 if stone else NULL_VERTEX
        self.size = 1 if stone else NULL_VERTEX
        self.v_atr = NULL_VERTEX
        self.libs.clear()

    def add(self, v):
        # add liberty at v
        if v not in self.libs:
            self.libs.add(v)
            self.lib_cnt += 1
            self.v_atr = v

    def sub(self, v):
        # remove liberty at v
        if v in self.libs:
            self.libs.remove(v)
            self.lib_cnt -= 1

    def merge(self, other):
        # merge with aother stone group
        self.libs |= other.libs
        self.lib_cnt = len(self.libs)
        self.size += other.size
        if self.lib_cnt == 1:
            for lib in self.libs:
                self.v_atr = lib

class Board(object):
    def __init__(self, board_size=BOARD_SIZE, komi=KOMI):
        self.color = np.full(NUM_VERTICES, INVLD) # stone color
        self.sg = [StoneGroup() for _ in range(NUM_VERTICES)]  # stone groups
        self.reset(board_size, komi)

    def reset(self, board_size, komi):
        self.board_size = board_size;
        self.num_intersections = self.board_size ** 2
        self.num_vertices = (self.board_size+2) ** 2
        self.komi = komi
        ebsize = board_size+2
        self.dir4 = [1, ebsize, -1, -ebsize]
        self.diag4 = [1 + ebsize, ebsize - 1, -ebsize - 1, 1 - ebsize]

        for idx in range(self.num_intersections):
            self.color[self.index_to_vertex(idx)] = EMPTY  # empty

        self.id = np.arange(NUM_VERTICES)  # id of stone group
        self.next = np.arange(NUM_VERTICES)  # next position in the same group
        for i in range(NUM_VERTICES):
            self.sg[i].clear(stone=False)

        self.num_passes = 0
        self.ko = NULL_VERTEX  # illegal position due to Ko
        self.to_move = BLACK  # black
        self.move_cnt = 0  # move count
        self.last_move = NULL_VERTEX  # last move
        self.remove_cnt = 0  # removed stones count
        self.history = []

    def copy(self):
        b_cpy = Board(self.board_size, self.komi)
        b_cpy.color = np.copy(self.color)
        b_cpy.id = np.copy(self.id)
        b_cpy.next = np.copy(self.next)
        for i in range(NUM_VERTICES):
            b_cpy.sg[i].lib_cnt = self.sg[i].lib_cnt
            b_cpy.sg[i].size = self.sg[i].size
            b_cpy.sg[i].v_atr = self.sg[i].v_atr
            b_cpy.sg[i].libs |= self.sg[i].libs

        b_cpy.num_passes = self.num_passes
        b_cpy.ko = self.ko
        b_cpy.to_move = self.to_move
        b_cpy.move_cnt = self.move_cnt
        b_cpy.last_move = self.last_move
        b_cpy.remove_cnt = self.remove_cnt

        for h in self.history:
            b_cpy.history.append(h)
        return b_cpy

    def remove(self, v):
        # remove stone group including stone at v
        v_tmp = v
        while 1:
            self.remove_cnt += 1
            self.color[v_tmp] = 2  # empty
            self.id[v_tmp] = v_tmp  # reset id
            for d in self.dir4:
                nv = v_tmp + d
                # add liberty to neighbor groups
                self.sg[self.id[nv]].add(v_tmp)
            v_next = self.next[v_tmp]
            self.next[v_tmp] = v_tmp
            v_tmp = v_next
            if v_tmp == v:
                break  # finish when all stones are removed

    def merge(self, v1, v2):
        # merge stone groups at v1 and v2
        id_base = self.id[v1]
        id_add = self.id[v2]
        if self.sg[id_base].size < self.sg[id_add].size:
            id_base, id_add = id_add, id_base  # swap
        self.sg[id_base].merge(self.sg[id_add])

        v_tmp = id_add
        while 1:
            self.id[v_tmp] = id_base  # change id to id_base
            v_tmp = self.next[v_tmp]
            if v_tmp == id_add:
                break
        # swap next id for circulation
        self.next[v1], self.next[v2] = self.next[v2], self.next[v1]

    def place_stone(self, v):
        self.color[v] = self.to_move
        self.id[v] = v
        self.sg[self.id[v]].clear(stone=True)
        for d in self.dir4:
            nv = v + d
            if self.color[nv] == 2:
                self.sg[self.id[v]].add(nv)  # add liberty
            else:
                self.sg[self.id[nv]].sub(v)  # remove liberty
        # merge stone groups
        for d in self.dir4:
            nv = v + d
            if self.color[nv] == self.to_move and self.id[nv] != self.id[v]:
                self.merge(v, nv)
        # remove opponent's stones
        self.remove_cnt = 0
        for d in self.dir4:
            nv = v + d
            if self.color[nv] == int(self.to_move == 0) and \
                    self.sg[self.id[nv]].lib_cnt == 0:
                self.remove(nv)

    def legal(self, v):
        if v == PASS:
            return True
        elif v == self.ko or self.color[v] != 2:
            return False

        stone_cnt = [0, 0]
        atr_cnt = [0, 0]
        for d in self.dir4:
            nv = v + d
            c = self.color[nv]
            if c == 2:
                return True
            elif c <= 1:
                stone_cnt[c] += 1
                if self.sg[self.id[nv]].lib_cnt == 1:
                    atr_cnt[c] += 1

        return (atr_cnt[int(self.to_move == 0)] != 0 or
                atr_cnt[self.to_move] < stone_cnt[self.to_move])

    def play(self, v):
        if not self.legal(v):
            return False
        else:
            if v == PASS:
                self.num_passes += 1
                self.ko = NULL_VERTEX
            else:
                self.place_stone(v)
                id = self.id[v]
                self.ko = NULL_VERTEX
                if self.remove_cnt == 1 and \
                        self.sg[id].lib_cnt == 1 and \
                        self.sg[id].size == 1:
                    self.ko = self.sg[id].v_atr
                self.num_passes = 0

        self.last_move = v
        self.history.append(copy.deepcopy(self.color))
        self.to_move = int(self.to_move == 0)
        self.move_cnt += 1

        return True

    def compute_reach_color(self, color):
        queue = []
        reachable = 0
        buf = [False] * NUM_VERTICES
        for v in range(NUM_VERTICES):
            if self.color[v] == color:
                reachable += 1
                buf[v] = True
                queue.append(v)

        while len(queue) != 0:
            v = queue.pop()
            for d in self.dir4:
                nv = v + d
                if self.color[nv] == color and buf[nv] == False:
                    reachable += 1
                    queue.append(nv)
                    buf[nv] = True
        return reachable

    def final_score(self):
        return self.compute_reach_color(BLACK) - self.compute_reach_color(WHITE) - self.komi

    def showboard(self):
        def get_xlabel(bsize):
            line_str = "  "
            for x in range(bsize):
                line_str += " " + X_LABELS[x] + " "
            return line_str + "\n"
        out = str()
        out += get_xlabel(self.board_size)

        for y in range(0, self.board_size)[::-1]:  # 9, 8, ..., 1
            line_str = str(y+1) if y >= 9 else " " + str(y+1)
            for x in range(0, self.board_size):
                v = self.get_vertex(x, y)
                x_str = " . "
                color = self.color[v]
                if color <= 1:
                    stone_str = "O" if color == WHITE else "X"
                    if v == self.last_move:
                        x_str = "[" + stone_str + "]"
                    else:
                        x_str = " " + stone_str + " "
                line_str += x_str
            line_str += str(y+1) if y >= 10 else " " + str(y+1)
            out += (line_str + "\n")

        out += get_xlabel(self.board_size)
        return out + "\n"

    def get_x(self, v):
        return v % (self.board_size+2) - 1

    def get_y(self, v):
        return v // (self.board_size+2) - 1

    def get_vertex(self, x, y):
        return (y+1) * (self.board_size+2) + (x+1)
        
    def get_index(self, x, y):
        return y * self.board_size + x

    def vertex_to_index(self, v):
        return self.get_index(self.get_x(v), self.get_y(v))
        
    def index_to_vertex(self, idx):
        return self.get_vertex(idx % self.board_size, idx // self.board_size)

    def vertex_to_text(self, vtx):
        if vtx == PASS:
            return "pass"
        elif vtx == RESIGN:
            return "resign"
        
        x = self.get_x(vtx)
        y = self.get_y(vtx)
        offset = 1 if x >= 8 else 0
        return "".join([chr(x + ord('A') + offset), str(y+1)])

    def get_features(self):
        my_color = self.to_move
        opp_color = (self.to_move + 1) % 2
        past = min(PAST_MOVES, len(self.history))
        
        features = np.zeros((INPUT_CHANNELS, self.num_intersections))
        for p in range(past):
            h = self.history[len(self.history) - p - 1]
            for v in range(self.num_vertices):
                c  = h[v]
                if c == my_color:
                    features[p*2, self.vertex_to_index(v)] = 1
                elif c == opp_color:
                    features[p*2+1, self.vertex_to_index(v)] = 1
        features[INPUT_CHANNELS - 2 + self.to_move, :] = 1
        return np.reshape(features, (INPUT_CHANNELS, self.board_size, self.board_size))
