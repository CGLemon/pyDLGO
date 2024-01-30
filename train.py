from network import Network
from config import BOARD_SIZE, INPUT_CHANNELS
from board import Board, PASS, BLACK, WHITE, INVLD, NUM_INTESECTIONS
from lazy_loader import LazyLoader, LoaderFlag

import sgf, argparse
import copy, random, time, os, shutil, glob
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim

CACHE_DIR = "data-cache"

def gather_filenames():
    def gather_recursive_files(root):
        l = list()
        for name in glob.glob(os.path.join(root, "*")):
            if os.path.isdir(name):
                l.extend(gather_recursive_files(name))
            else:
                l.append(name)
        return l
    return gather_recursive_files(CACHE_DIR)

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
        self.inputs = None # should be numpy array, shape is [INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE]
        self.policy = None # should be integer, range is 0 ~ NUM_INTESECTIONS
        self.value = None # should be float, range is -1 ~ 1
        self.to_move = None

    def __str__(self):
        out = str()
        out += "policy: {p} | value: {v}\n".format(p=self.policy, v=self.value)
        return out

    def do_symmetry(self, symm=None):
        assert self.policy != None, ""

        if symm is None:
            symm = int(np.random.choice(8, 1)[0])

        for i in range(INPUT_CHANNELS-2): # last 2 channels is side to move.
            p = self.inputs[i]
            self.inputs[i][:][:] = get_symmetry_plane(symm, p)[:][:]

        if self.policy != NUM_INTESECTIONS:
            buf = np.zeros(NUM_INTESECTIONS)
            buf[self.policy] = 1
            buf = get_symmetry_plane(symm, np.reshape(buf, (BOARD_SIZE, BOARD_SIZE)))
            self.policy = int(np.argmax(buf))

class StreamLoader:
    def __init__(self):
        pass

    def func(self, filename):
        chunk = np.load(filename)
        sub_buffer = []

        inputs_buf = chunk['i']
        policy_buf = chunk['p']
        value_buf  = chunk['v']
        to_move_buf = chunk['t']

        size = to_move_buf.shape[0]
        for i in range(size):
            data = Data()
            data.inputs = inputs_buf[i]
            data.policy = policy_buf[i]
            data.value = value_buf[i]
            data.to_move = to_move_buf[i]
            data.do_symmetry()
            sub_buffer.append(data)
        random.shuffle(sub_buffer)
        return sub_buffer

class StreamParser:
    def __init__(self):
        pass

    def func(self, sub_buffer):
        if len(sub_buffer) == 0:
            return None
        return sub_buffer.pop()

class BatchGenerator:
    def __init__(self):
        pass

    def func(self, data_list):
        i_batch = []
        p_batch = []
        v_batch = []
        for d in data_list:
            i_batch.append(d.inputs)
            p_batch.append(d.policy)
            v_batch.append(d.value)
        i_t_batch = torch.tensor(np.array(i_batch)).float()
        p_t_batch = torch.tensor(np.array(p_batch)).long()
        v_t_batch = torch.tensor(np.array(v_batch)).float()

        return i_t_batch, p_t_batch, v_t_batch

# Load the SGF files and save the training data to the disk.
class DataChopper:
    def  __init__(self, dir_name, games_per_chunk, num_sgfs):
        self.cache_dir = CACHE_DIR
        self.num_data = 0
        self._chop_data(dir_name, games_per_chunk, num_sgfs)

    def __del__(self):
        # Do not delete the training data in the cache dir. We may
        # use them next time.
        pass

    def _chop_data(self, dir_name, games_per_chunk, num_sgfs):
        # Load the SGF files and tranfer them to training data.
        sgf_games = sgf.parse_from_dir(dir_name)
        total_steps = min(len(sgf_games), num_sgfs)
        games_per_chunk = max(games_per_chunk, 1)

        print("imported {} SGF files".format(total_steps))

        if os.path.isdir(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)
        os.mkdir(self.cache_dir)

        chunk_cnt = 0
        buf = []

        for s in range(total_steps):
            game = sgf_games[s]
            temp = self._process_one_game(game)

            buf.extend(temp)

            if (s+1) % games_per_chunk == 0:
                print("parsed {:.2f}% games".format(100 * (s+1)/total_steps))
                self._save_chunk(buf, chunk_cnt)
                chunk_cnt += 1
                buf = []

        # There still some data in the buffer. Save them.
        if len(buf) != 0:
            print("parsed {:.2f}% games".format(100))
            self._save_chunk(buf, chunk_cnt)

    def _save_chunk(self, buf, cnt):
        # Save the training data to the disk.
        size = len(buf)

        # Shuffle it.
        random.shuffle(buf)

        inputs_buf = np.zeros((size, INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        policy_buf = np.zeros((size), dtype=np.int32)
        value_buf = np.zeros((size, 1), dtype=np.float32)
        to_move_buf = np.zeros((size), dtype=np.int8)

        self.num_data += size

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

class TrainingPipe:
    VALUE_LOSS_SCALE = 0.25

    def __init__(self, dir_name, rate, buffer_size, batch_size, games_per_chunk, num_sgfs):
        self.network = Network(BOARD_SIZE)
        self.network.trainable(True)

        # Leave two cores for training pipe.
        self.num_workers = max(min(os.cpu_count(), 16) - 2 , 1)

        print("Use {n} workers for loader.".format(n=self.num_workers))

        if dir_name is not None:
            self.data_chopper = DataChopper(dir_name, games_per_chunk, num_sgfs)

        # We use the customized loader instead of pyTorch loader in
        # order to improve the randomness of data.
        self.flag = LoaderFlag()
        self.loader = LazyLoader(
            filenames = gather_filenames(),
            stream_loader = StreamLoader(),
            stream_parser = StreamParser(),
            batch_generator = BatchGenerator(),
            down_sample_rate = rate,
            num_workers = self.num_workers,
            buffer_size = buffer_size,
            batch_size = batch_size,
            flag = self.flag
        )
        batch = next(self.loader) # init the loader

    def running(self, max_steps, verbose_steps, learning_rate, decay_steps, decay_factor, noplot):
        cross_entry = nn.CrossEntropyLoss()
        mse_loss = nn.MSELoss()

        # SGD instead of Adam. Seemd the SGD performance
        # is better Adam.
        optimizer = optim.SGD(self.network.parameters(),
                              lr=learning_rate,
                              momentum=0.9,
                              nesterov=True,
                              weight_decay=1e-3)

        p_running_loss = 0
        v_running_loss = 0
        steps = 0
        keep_running = True
        running_loss_record = []
        clock_time = time.time()

        while steps < max_steps:
            if decay_steps is not None:
                if (steps+1) % decay_steps == 0:
                    print("Drop the learning rate from {} to {}.".format(
                              learning_rate,
                              learning_rate * decay_factor
                              ))
                    learning_rate = learning_rate * decay_factor
                    for param in optimizer.param_groups:
                        param["lr"] = learning_rate

            # First, get the batch data.
            inputs, target_p, target_v = next(self.loader)

            # Second, Move the data to GPU memory if we use it.
            if self.network.use_gpu:
                inputs = inputs.to(self.network.gpu_device)
                target_p = target_p.to(self.network.gpu_device)
                target_v = target_v.to(self.network.gpu_device)

            # Third, compute the network result.
            p, v = self.network(inputs)

            # Fourth, compute the loss result and update network.
            p_loss = cross_entry(p, target_p)
            v_loss = mse_loss(v, target_v)
            loss = p_loss + self.VALUE_LOSS_SCALE * v_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Accumulate running loss.
            p_running_loss += p_loss.item()
            v_running_loss += v_loss.item()

            # Fifth, dump training verbose.
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

        self.flag.set_stop_flag()
        try:
            inputs, target_p, target_v = next(self.loader)
        except StopIteration:
            pass

        print("Training is over.");
        if not noplot:
            # sixth plot the running loss graph.
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
        # TODO: We should save the optimizer status too.
        self.network.save_pt(name)

    def load_weights(self, name):
        if name != None:
            self.network.load_pt(name)

def valid_args(args):
    result = True

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
                        help="The input SGF files directory. Will use data cache if set None.", type=str)
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
    parser.add_argument("-g", "--games-per-chunk", metavar="<integer>",
                        help="The SGF games per chunk.", type=int, default=50)
    parser.add_argument("-i", "--imported-games", metavar="<integer>",
                        help="The max number of imported games.", type=int, default=10240000)
    parser.add_argument("-r", "--rate", metavar="<int>",
                        help="The down sample rate.", type=int, default=0)
    parser.add_argument("--load-weights", metavar="<string>",
                        help="The inputs weights name.", type=str)
    parser.add_argument("--noplot", action="store_true",
                        help="Disable plotting.", default=False)
    parser.add_argument("--buffer-size", metavar="<integer>",
                        help="The buffer size of lazy loader.", type=int, default=512000)
    parser.add_argument("--lr-decay-steps", metavar="<integer>",
                        help="Reduce the learning rate every X steps.", type=int, default=None)
    parser.add_argument("--lr-decay-factor", metavar="<float>",
                        help="The learning rate decay multiple factor.", type=float, default=0.1)

    args = parser.parse_args()
    if valid_args(args):
        pipe = TrainingPipe(args.dir, args.rate, args.buffer_size,
                            args.batch_size, args.games_per_chunk, args.imported_games)
        pipe.load_weights(args.load_weights)
        pipe.running(
            args.steps,
            args.verbose_steps,
            args.learning_rate,
            args.lr_decay_steps,
            args.lr_decay_factor,
            args.noplot
        )
        pipe.save_weights(args.weights_name)
