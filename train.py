# -*- coding: utf-8 -*-

from network import Network
from config import BOARD_SIZE, KOMI, INPUT_CHANNELS, PAST_MOVES
from board import Board, PASS, BLACK, WHITE, EMPTY, INVLD, NUM_INTESECTIONS

import sgf, argparse
import copy, random
import numpy as np

class Chunk:
    def __init__(self):
        self.inputs = None
        self.policy = None
        self.value = None
        self.to_move = None

    def __str__(self):
        out = str()
        out += "policy: {p} | value: {v}\n".format(p=self.policy, v=self.value)
        return out

class DataSet:
    def  __init__(self, dir_name):
        self.buffer = []
        self.load_data(dir_name)

    def load_data(self, dir_name):
        sgf_games = sgf.parser_from_dir(dir_name)
        for game in sgf_games:
            temp = self.process_one_game(game)
            self.buffer.extend(temp)

    def get_batch(self, batch_size=512):
        s = random.sample(self.buffer, k=batch_size)
        inputs_batch = []
        policy_batch = []
        value_batch = []
        for chunk in s:
            inputs_batch.append(chunk.inputs)
            policy_batch.append(chunk.policy)
            value_batch.append([chunk.value])
        inputs_batch = np.array(inputs_batch)
        policy_batch = np.array(policy_batch)
        value_batch = np.array(value_batch)
        return inputs_batch, policy_batch, value_batch

    def process_one_game(self, game):
        temp = []
        winner = None
        board = Board(BOARD_SIZE)
        for node in game:
            color = INVLD
            move = None
            if "W" in node.properties:
                color = WHITE
                move = node.properties["W"][0]
            elif "B" in node.properties:
                color = BLACK
                move = node.properties["B"][0]
            elif "RE" in node.properties:
                result = node.properties["RE"][0]
                if "B+" in result:
                    winner = BLACK
                elif "W+" in result:
                    winner = WHITE
            if color != INVLD:
                chunk = Chunk()
                chunk.inputs = board.get_features()
                chunk.to_move = color
                chunk.policy = self.do_text_move(board, color, move)
                temp.append(chunk)

        for chunk in temp:
            if winner == None:
                chunk.value = 0
            elif winner == chunk.to_move:
                chunk.value = 1
            elif winner != chunk.to_move:
                chunk.value = -1
        return temp

    def do_text_move(self, board, color, move):
        board.to_move = color
        policy = None
        vtx = None
        if len(move) == 0 or move == "tt":
           vtx = PASS
           policy = NUM_INTESECTIONS
        else:
            x = ord(move[0]) - ord('a')
            y = ord(move[1]) - ord('a')
            vtx = board.get_vertex(x, y)
            policy = board.get_index(x,y)
        board.play(vtx)
        return policy

class TrainingPipe:
    def __init__(self, dir_name):
        self.net = Network(BOARD_SIZE)
        self.data_set = DataSet(dir_name)
        
    def running(self, step, batch_size, learning_rate):
        cross_entry = nn.CrossEntropyLoss()
        mse_loss = nn.MSELoss()
        optimizer = optim.Adam(lr=leaning_rate, weight_decay=1e-4)
        verbose_step = 100
        p_running_loss = 0
        v_running_loss = 0

        for _ in range(step):
            i, target_p, target_v = data_set.get_batch(batch_size)
        
            optimizer.zero_grad()
            p, v = net(inputs)

            p_loss = cross_entry(p, target_p)
            v_loss = mse_loss(v, target_v)
            loss = p_loss + v_loss
            loss.backward()

            p_running_loss += p_loss.item()
            v_running_loss += v_loss.item()

            if (step+1) % verbose_step == 0:
                print("step: {s} -> policy loss: {p} | value loss: {v}\n",
                          s=step,
                          p=p_running_loss/verbose_step,
                          v=v_running_loss/verbose_step)
                p_running_loss = 0
                v_running_loss = 0

    def save_weights(self, name):
        self.net.save_pt(name + ".pt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="The input directory", type=str)
    parser.add_argument("-s", "--step", help="The training step", type=int)
    parser.add_argument("-b", "--batch-size", type=int)
    parser.add_argument("-l", "--learning-rate", type=float)
    parser.add_argument("-w", "--weights-name", type=float)

    args = parser.parse_args()
    pipe = TrainingPipe(args.dir)
    pipe.running(args.step, args.batch_size, args.learning_rate)
    pipe.save_weights(args.weights_name)
