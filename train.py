from network import Network
from config import BOARD_SIZE, INPUT_CHANNELS
from board import Board, PASS, BLACK, WHITE, INVLD, NUM_INTESECTIONS

import sgf, argparse
import copy, random, time, os, shutil, glob
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

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

class Data:
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


class DataSource:
    def  __init__(self):
        self.cache_dir = "data-cache"
        self.buffer = []
        self.chunks = []
        self.done = glob.glob(os.path.join(self.cache_dir, "*"))

    def _chunk_to_buf(self, chunk):
        inputs_buf = chunk['i']
        policy_buf = chunk['p']
        value_buf = chunk['v']
        to_move_buf = chunk['t']

        size = to_move_buf.shape[0]
        for i in range(size):
            data = Data()
            data.inputs = inputs_buf[i]
            data.policy = policy_buf[i]
            data.value = value_buf[i]
            data.to_move = to_move_buf[i]
            self.buffer.append(data)

    def next(self):
        if len(self.buffer) == 0:
            if len(self.chunks) == 0:
                self.chunks, self.done = self.done, self.chunks
                random.shuffle(self.chunks)

            filename = self.chunks.pop()
            self.done.append(filename)

            chunk = np.load(filename)
            self._chunk_to_buf(chunk)
        return self.buffer.pop()

class DataChopper:
    def  __init__(self, dir_name):
        self.cache_dir = "data-cache"
        self._chop_data(dir_name)

    def __del__(self):
        pass

    def _chop_data(self, dir_name):
        sgf_games = sgf.parse_from_dir(dir_name)
        total = len(sgf_games)

        print("imported {} SGF files".format(total))

        if os.path.isdir(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)

        os.mkdir(self.cache_dir)

        cnt = 0
        steps = 0
        chop_steps = max(total//100, 1)
        buf = []

        for game in sgf_games:
            steps += 1
            temp = self._process_one_game(game)

            buf.extend(temp)

            if steps % chop_steps == 0:
                print("parsed {:.2f}% games".format(100 * steps/total))
                self._save_chunk(buf, cnt)
                cnt += 1
                buf = []

        if len(buf) != 0:
            print("parsed {:.2f}% games".format(100 * steps/total))
            self._save_chunk(buf, cnt)

    def _save_chunk(self, buf, cnt):
        size = len(buf)

        inputs_buf = np.zeros((size, INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE))
        policy_buf = np.zeros((size))
        value_buf = np.zeros((size, 1))
        to_move_buf = np.zeros((size))

        for i in range(size):
            data = buf[i]
            inputs_buf[i, :] = data.inputs[:]
            policy_buf[i] = data.policy
            value_buf[i, 0] = data.value
            to_move_buf[i] = data.to_move

        filenmae = os.path.join(self.cache_dir, "chunk_{}.npz".format(cnt))
        np.savez_compressed(filenmae, i=inputs_buf, p=policy_buf, v=value_buf, t=to_move_buf)

    def _process_one_game(self, game):
        # Collect training data from one SGF game.

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
                data = Data()
                data.inputs = board.get_features()
                data.to_move = color
                data.policy = self._do_text_move(board, color, move)
                temp.append(data)

        for data in temp:
            if winner == None:
                data.value = 0
            elif winner == data.to_move:
                data.value = 1
            elif winner != data.to_move:
                data.value = -1
        return temp

    def _do_text_move(self, board, color, move):
        # Play next move and return the policy data.

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

class DataSet:
    def __init__(self, num_workers):
        self.dummy_size = 0
        self.data_loaders = []
        self.data_scrs = []

        num_workers = max(num_workers, 1)
        for _ in range(num_workers):
            self.data_scrs.append(DataSource())

    def __getitem__(self, idx):
        worker_info = torch.utils.data.get_worker_info()
        worker_id = None
        if worker_info == None:
            worker_id = 0
        else:
            worker_id = worker_info.id

        data = self.data_scrs[worker_id].next()
        return (
            torch.tensor(data.inputs).float(),
            torch.tensor(data.policy).long(),
            torch.tensor(data.value).float()
        )


    def __len__(self):
        return self.dummy_size

class TrainingPipe:
    def __init__(self, dir_name, use_cache):
        self.network = Network(BOARD_SIZE)
        self.network.trainable()

        self.num_workers = max(min(os.cpu_count(), 16) - 2 , 0)
        self.steps_per_epoch = 2000

        if not use_cache:
            self.data_chopper = DataChopper(dir_name)
        self.data_set = DataSet(self.num_workers)
        
    def running(self, max_steps, verbose_steps, batch_size, learning_rate, noplot):
        cross_entry = nn.CrossEntropyLoss()
        mse_loss = nn.MSELoss()
        optimizer = optim.Adam(self.network.parameters(), lr=learning_rate, weight_decay=1e-4)
        p_running_loss = 0
        v_running_loss = 0
        steps = 0
        keep_running = True
        running_loss_record = []
        clock_time = time.time()

        while keep_running:
            self.data_set.dummy_size = self.steps_per_epoch * batch_size

            train_data = DataLoader(
                self.data_set,
                num_workers=self.num_workers,
                batch_size=batch_size
            )

            for _, batch in enumerate(train_data):
                # First, get the batch data.
                inputs, target_p, target_v = batch

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
                if (steps+1) % verbose_steps == 0:
                    elapsed = time.time() - clock_time
                    rate = verbose_steps/elapsed
                    remaining_steps = max_steps - steps
                    estimate_remaining_time = int(remaining_steps/rate)
                    print("{} steps: {}/{}, {:.2f}% -> policy loss: {:.4f}, value loss: {:.4f} | rate: {:.2f}(steps/sec), estimate: {}(sec)".format(
                              get_currtime(),
                              steps+1,
                              max_steps,
                              100 * ((steps+1)/max_steps),
                              p_running_loss/verbose_steps,
                              v_running_loss/verbose_steps,
                              rate,
                              estimate_remaining_time))
                    running_loss_record.append((steps+1, p_running_loss/verbose_steps, v_running_loss/verbose_steps))
                    p_running_loss = 0
                    v_running_loss = 0
                    clock_time = time.time()

                steps += 1
                if steps >= max_steps:
                    keep_running = False
                    break

        print("Training is over.");
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

        y_upper = max(max(p_running_loss), max(v_running_loss))

        plt.plot(step, p_running_loss, label="policy loss")
        plt.plot(step, v_running_loss, label="value loss")
        plt.ylabel("loss")
        plt.xlabel("steps")
        plt.ylim([0, y_upper * 1.1])
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
    if args.steps == None:
        print("Must to give the argument --steps <integer>")
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
                        help="The input SGF files directory", type=str)
    parser.add_argument("-s", "--steps", metavar="<integer>",
                        help="Terminate after these steps", type=int)
    parser.add_argument("-v", "--verbose-steps", metavar="<integer>",
                        help="Dump verbose on every X steps.", type=int, default=1000)
    parser.add_argument("-b", "--batch-size", metavar="<integer>",
                        help="The batch size number.", type=int)
    parser.add_argument("-l", "--learning-rate", metavar="<float>",
                        help="The learning rate.", type=float)
    parser.add_argument("-w", "--weights-name", metavar="<string>",
                        help="The output weights name.", type=str)
    parser.add_argument("-c", "--cache", action="store_true",
                        help="Use the data cache without parsing new SGF files.", default=False)
    parser.add_argument("--load-weights", metavar="<string>",
                        help="The inputs weights name.", type=str)
    parser.add_argument("--noplot", action="store_true",
                        help="Disable plotting.", default=False)

    args = parser.parse_args()
    if valid_args(args):
        pipe = TrainingPipe(args.dir, args.cache)
        pipe.load_weights(args.load_weights)
        pipe.running(args.steps, args.verbose_steps, args.batch_size, args.learning_rate, args.noplot)
        pipe.save_weights(args.weights_name)
