from network import Network
from config import BOARD_SIZE, KOMI, INPUT_CHANNELS, PAST_MOVES
from board import Board, PASS, BLACK, WHITE, EMPTY, INVLD, NUM_INTESECTIONS

import sgf, argparse
import copy, random, time
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim

def get_currtime():
    lt = time.localtime(time.time())
    return "[{y}-{m}-{d} {h:02d}:{mi:02d}:{s:02d}]".format(
               y=lt.tm_year, m=lt.tm_mon,  d=lt.tm_mday, h=lt.tm_hour, mi=lt.tm_min, s=lt.tm_sec)

def get_symmetry_plane(symm, plane):
    use_flip = False
    if symm // 4 != 0:
        use_flip = True
    symm = symm % 4

    transformed = np.rot90(plane, symm)

    if use_flip:
        transformed = np.flip(transformed, 1)
    return transformed

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

    def do_symmetry(self, symm=None):
        assert self.policy != None, ""

        if symm == None:
            symm = int(np.random.choice(8, 1)[0])

        for i in range(INPUT_CHANNELS-2): # last 2 channels is side to move.
            p = self.inputs[i]
            self.inputs[i][:][:] = get_symmetry_plane(symm, p)[:][:]

        if self.policy != NUM_INTESECTIONS:
            buf = np.zeros(NUM_INTESECTIONS)
            buf[self.policy] = 1
            buf = get_symmetry_plane(symm, np.reshape(buf, (BOARD_SIZE, BOARD_SIZE)))
            self.policy = int(np.argmax(buf))

class DataSet:
    def  __init__(self, dir_name):
        self.buffer = []
        self._load_data(dir_name)

    # Collect training data from sgf dirctor.
    def _load_data(self, dir_name):
        sgf_games = sgf.parse_from_dir(dir_name)
        total = len(sgf_games)
        step = 0
        verbose_step = 1000
        print("total {} games".format(total))
        for game in sgf_games:
            step += 1
            temp = self._process_one_game(game)
            self.buffer.extend(temp)
            if step % verbose_step == 0:
                print("parsed {:.2f}% games".format(100 * step/total))
        if total % verbose_step != 0:
            print("parsed {:.2f}% games".format(100 * step/total))

    # Collect training data from one sgf game.
    def _process_one_game(self, game):
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
                chunk.policy = self._do_text_move(board, color, move)
                temp.append(chunk)

        for chunk in temp:
            if winner == None:
                chunk.value = 0
            elif winner == chunk.to_move:
                chunk.value = 1
            elif winner != chunk.to_move:
                chunk.value = -1
        return temp

    def _do_text_move(self, board, color, move):
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
            policy = board.get_index(x, y)
        board.play(vtx)
        return policy

    def get_batch(self, batch_size):
        s = random.sample(self.buffer, k=batch_size)
        inputs_batch = []
        policy_batch = []
        value_batch = []
        for chunk in s:
            chunk.do_symmetry()
            inputs_batch.append(chunk.inputs)
            policy_batch.append(chunk.policy)
            value_batch.append([chunk.value])
        inputs_batch = np.array(inputs_batch)
        policy_batch = np.array(policy_batch)
        value_batch = np.array(value_batch)
        return (
            torch.tensor(inputs_batch).float(),
            torch.tensor(policy_batch).long(),
            torch.tensor(value_batch).float()
        )

class TrainingPipe:
    def __init__(self, dir_name):
        self.network = Network(BOARD_SIZE)
        self.network.trainable()

        # Prepare the data set from sgf files.
        self.data_set = DataSet(dir_name)
        
    def running(self, max_step, verbose_step, batch_size, learning_rate, noplot):
        cross_entry = nn.CrossEntropyLoss()
        mse_loss = nn.MSELoss()
        optimizer = optim.Adam(self.network.parameters(), lr=learning_rate, weight_decay=1e-4)
        p_running_loss = 0
        v_running_loss = 0
        running_loss_record = []
        clock_time = time.time()

        for step in range(max_step):
            # First, get the batch data.
            inputs, target_p, target_v = self.data_set.get_batch(batch_size)

            # Second, Move the data to GPU memory if we use it.
            if self.network.use_gpu:
                inputs = inputs.to(self.network.gpu_device)
                target_p = target_p.to(self.network.gpu_device)
                target_v = target_v.to(self.network.gpu_device)

            # Third, compute network result.
            p, v = self.network(inputs)

            # Fourth, compute loss result and update network.
            p_loss = cross_entry(p, target_p)
            v_loss = mse_loss(v, target_v)
            loss = p_loss + v_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            p_running_loss += p_loss.item()
            v_running_loss += v_loss.item()

            # Fifth, dump verbose.
            if (step+1) % verbose_step == 0:
                elapsed = time.time() - clock_time
                rate = verbose_step/elapsed
                remaining_step = max_step - step
                estimate_remaining_time = int(remaining_step/rate)
                print("{} steps: {}/{}, {:.2f}% -> policy loss: {:.4f}, value loss: {:.4f} | rate: {:.2f}(step/sec), estimate: {}(sec)".format(
                          get_currtime(),
                          step+1,
                          max_step,
                          100 * ((step+1)/max_step),
                          p_running_loss/verbose_step,
                          v_running_loss/verbose_step,
                          rate,
                          estimate_remaining_time))
                running_loss_record.append((step+1, p_running_loss/verbose_step, v_running_loss/verbose_step))
                p_running_loss = 0
                v_running_loss = 0
                clock_time = time.time()
        print("Trainig is over.");
        if not noplot:
            self.plot_loss(running_loss_record)

    def plot_loss(self, record):
        p_running_loss = []
        v_running_loss = []
        step = []
        for (s, p, v) in record:
            p_running_loss.append(p)
            v_running_loss.append(v)
            step.append(s)
        plt.plot(step, p_running_loss, label="policy loss")
        plt.plot(step, v_running_loss, label="value loss")
        plt.ylabel("loss")
        plt.xlabel("steps")
        plt.legend()
        plt.show()

    def save_weights(self, name):
        self.network.save_pt(name)

    def load_weights(self, name):
        if name != None:
            self.network.load_pt(name)

def valid_args(args):
    result = True

    if args.dir == None:
        print("Must to give the argument --dir <string>")
        result = False
    if args.weights_name == None:
        print("Must to give the argument --weights-name <string>")
        result = False
    if args.step == None:
        print("Must to give the argument --step <integer>")
        result = False
    if args.batch_size == None:
        print("Must to give the argument --batch-size <integer>")
        result = False
    if args.learning_rate == None:
        print("Must to give the argument --learning-rate <float>")
        result = False

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", metavar="<string>",
                        help="The input directory", type=str)
    parser.add_argument("-s", "--step", metavar="<integer>",
                        help="The training step", type=int)
    parser.add_argument("-v", "--verbose-step", metavar="<integer>",
                        help="Dump verbose in every X steps." , type=int, default=1000)
    parser.add_argument("-b", "--batch-size", metavar="<integer>", type=int)
    parser.add_argument("-l", "--learning-rate", metavar="<float>", type=float)
    parser.add_argument("-w", "--weights-name", metavar="<string>", type=str)
    parser.add_argument("--load-weights", metavar="<string>", type=str)
    parser.add_argument("--noplot", action="store_true", default=False)

    args = parser.parse_args()
    if valid_args(args):
        pipe = TrainingPipe(args.dir)
        pipe.load_weights(args.load_weights)
        pipe.running(args.step, args.verbose_step, args.batch_size, args.learning_rate, args.noplot)
        pipe.save_weights(args.weights_name)
