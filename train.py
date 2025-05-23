from network import Network
from config import BOARD_SIZE, INPUT_CHANNELS
from board import Board, PASS, BLACK, WHITE, EMPTY, INVLD, NUM_INTESECTIONS

import sgf, argparse
import copy, time, os, shutil, glob
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim

CACHE_TRAIN_DIR = "tdata-cache"
CACHE_VALID_DIR = "vdata-cache"

def gather_filenames(dirname):
    def gather_recursive_files(root):
        l = list()
        for name in glob.glob(os.path.join(root, "*")):
            if os.path.isdir(name):
                l.extend(gather_recursive_files(name))
            else:
                l.append(name)
        return l
    return gather_recursive_files(root=dirname)

def get_currtime():
    lt = time.localtime(time.time())
    return "{y}-{m}-{d} {h:02d}:{mi:02d}:{s:02d}".format(
               y=lt.tm_year, m=lt.tm_mon,  d=lt.tm_mday, h=lt.tm_hour, mi=lt.tm_min, s=lt.tm_sec)

def get_weights_name(prefix):
    return "{}-{}.pt".format(prefix, get_currtime().replace(":", "-").replace(" ", "-"))

class Data:
    def __init__(self):
        self.inputs = None # should be numpy array, shape is [INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE]
        self.policy = None # should be integer, range is 0 ~ NUM_INTESECTIONS
        self.value = None # should be float, range is -1 ~ 1
        self.to_move = None

    def _get_symmetry_plane(self, symm, plane):
        use_flip = False
        if symm // 4 != 0:
            use_flip = True
        symm = symm % 4

        transformed = np.rot90(plane, symm)

        if use_flip:
            transformed = np.flip(transformed, 1)
        return transformed

    def do_symmetry(self, symm=None):
        assert self.policy != None, ""

        if symm is None:
            symm = int(np.random.choice(8, 1)[0])

        for i in range(INPUT_CHANNELS-2): # last 2 channels is side to move.
            p = self.inputs[i]
            self.inputs[i][:][:] = self._get_symmetry_plane(symm, p)[:][:]

        if self.policy != NUM_INTESECTIONS:
            buf = np.zeros(NUM_INTESECTIONS)
            buf[self.policy] = 1
            buf = self._get_symmetry_plane(symm, np.reshape(buf, (BOARD_SIZE, BOARD_SIZE)))
            self.policy = int(np.argmax(buf))

    def from_npfile(self, filename):
        npdata = np.load(filename)
        self.inputs = npdata["i"]
        self.policy = npdata["p"][0]
        self.value = npdata["v"][0]
        self.to_move = npdata["t"][0]

class Dataset(torch.utils.data.Dataset):
    def __init__(self, source_dir, num_virtual_samples=None):
        self.filenames = gather_filenames(source_dir)
        self.num_virtual_samples = num_virtual_samples \
            if num_virtual_samples is not None else len(self.filenames)

    def __len__(self):
        return self.num_virtual_samples

    def __getitem__(self, i):
        current_idx = i % len(self.filenames)
        data = Data()
        data.from_npfile(self.filenames[current_idx])
        data.do_symmetry()

        inputs = torch.tensor(data.inputs).float()
        policy = torch.tensor(data.policy).long()
        value = torch.tensor([data.value]).float()
        return inputs, policy, value

# Load the SGF files and save the training data to the disk.
class DataChopper:
    def  __init__(self, dir_name, num_sgfs):
        self.num_data = 0
        self._chop_data(dir_name, num_sgfs)

    def __del__(self):
        # Do not delete the training data in the cache dir. We may
        # use them next time.
        pass

    def _chop_data(self, dir_name, num_sgfs):
        # Load the SGF files and tranfer them to training data.
        sgf_games = sgf.parse_from_dir(dir_name)
        total_games = min(len(sgf_games), num_sgfs)

        print("imported {} SGF files".format(total_games))

        if os.path.isdir(CACHE_TRAIN_DIR):
            shutil.rmtree(CACHE_TRAIN_DIR, ignore_errors=True)
        os.makedirs(CACHE_TRAIN_DIR)

        if os.path.isdir(CACHE_VALID_DIR):
            shutil.rmtree(CACHE_VALID_DIR, ignore_errors=True)
        os.makedirs(CACHE_VALID_DIR)

        for s in range(total_games):
            game = sgf_games[s]
            buf = self._process_one_game(game)

            if (s+1) % (max(1, total_games//100)) == 0:
                print("parsed {:.2f}% games".format(100 * (s+1)/total_games))
            self._save_data(buf)
        print("done! parsed {:.2f}% games".format(100))

    def _save_data(self, buf):
        size = len(buf)

        for i in range(size):
            # Allocate data buffer
            inputs_buf = np.zeros((INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
            policy_buf = np.zeros((1), dtype=np.int32)
            value_buf = np.zeros((1), dtype=np.float32)
            to_move_buf = np.zeros((1), dtype=np.int8)

            # Fill the data buffer.
            data = buf[i]
            inputs_buf[:] = data.inputs[:]
            policy_buf[:] = data.policy
            value_buf[:] = data.value
            to_move_buf[:] = data.to_move

            # Save the date on disk.
            use_valid = int(np.random.choice(10, 1)[0]) == 0
            if use_valid:
                filename = os.path.join(CACHE_VALID_DIR, "data_{}.npz".format(self.num_data))
            else:
                filename = os.path.join(CACHE_TRAIN_DIR, "data_{}.npz".format(self.num_data))
            np.savez_compressed(filename, i=inputs_buf, p=policy_buf, v=value_buf, t=to_move_buf)
            self.num_data += 1

    def _process_one_game(self, game):
        # Collect training data from one SGF game.

        if game.board_size is not BOARD_SIZE:
            return list()

        temp = list()
        winner = game.winner
        board = Board(BOARD_SIZE)

        for color, move in game.history:
            data = Data()
            data.inputs = board.get_features()
            data.to_move = color
            if move:
                x, y = move
                data.policy = board.get_index(x, y)
                board.play(board.get_vertex(x, y))
            else:
                data.policy = board.num_intersections
                board.play(PASS)
            temp.append(data)

        for data in temp:
            if winner == EMPTY:
                data.value = 0
            elif winner == data.to_move:
                data.value = 1
            elif winner != data.to_move:
                data.value = -1
        return temp

def plot_loss(record):
    if len(record) <= 1:
        return

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

def load_checkpoint(network, optimizer, workspace):
    filenames = gather_filenames(workspace)
    if len(filenames) == 0:
        return network, optimizer, 0

    filenames.sort(key=os.path.getmtime, reverse=True)
    last_pt = filenames[0]

    state_dict = torch.load(last_pt, map_location=network.gpu_device, weights_only=True)
    network.load_state_dict(state_dict["network"])
    optimizer.load_state_dict(state_dict["optimizer"])
    steps = state_dict["steps"]
    return network, optimizer, steps

def save_checkpoint(network, optimizer, steps, workspace):
    state_dict = dict()
    state_dict["network"] = network.state_dict()
    state_dict["optimizer"] = optimizer.state_dict()
    state_dict["steps"] = steps
    torch.save(state_dict, os.path.join(workspace, "checkpoint-s{}.pt".format(steps)))

def training_process(args):
    # Set the network. Will push on GPU device later if it is
    # available.
    network = Network(BOARD_SIZE)
    network.trainable(True)

    # SGD instead of Adam. Seemd the SGD performance
    # is better than Adam.
    optimizer = optim.SGD(network.parameters(),
                          lr=args.learning_rate,
                          momentum=0.9,
                          nesterov=True,
                          weight_decay=1e-3)
    if not os.path.isdir(args.workspace):
        os.mkdir(args.workspace)
    network, optimizer, steps = load_checkpoint(network, optimizer, args.workspace)
    cross_entry = nn.CrossEntropyLoss()
    mse_loss = nn.MSELoss()

    if args.dir is not None:
        data_chopper = DataChopper(
            args.dir,
            args.imported_games
        )

    # Leave two cores for training pipe.
    num_workers = max(min(os.cpu_count(), 16) - 2 , 1) \
                      if args.num_workers is None else max(args.num_workers, 1)

    print("Use {n} workers for loader.".format(n=num_workers))

    data_loader = torch.utils.data.DataLoader(
        dataset=Dataset(CACHE_TRAIN_DIR, args.batch_size * args.steps),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=num_workers
    )

    print("Start training...");

    # init some basic parameters
    p_running_loss = 0
    v_running_loss = 0
    max_steps = steps + args.steps
    running_loss_record = []
    clock_time = time.time()

    for _, batch in enumerate(data_loader):
        if args.lr_decay_steps is not None:
            learning_rate = optimizer.param_groups[0]["lr"]
            if (steps+1) % args.lr_decay_steps == 0:
                print("Drop the learning rate from {} to {}.".format(
                          learning_rate,
                          learning_rate * args.lr_decay_factor
                          ))
                learning_rate = learning_rate * args.lr_decay_factor
                for param in optimizer.param_groups:
                    param["lr"] = learning_rate

        # First, get the batch data.
        inputs, target_p, target_v = batch

        # Second, Move the data to GPU memory if we use it.
        if network.use_gpu:
            inputs = inputs.to(network.gpu_device)
            target_p = target_p.to(network.gpu_device)
            target_v = target_v.to(network.gpu_device)

        # Third, compute the network result.
        p, v = network(inputs)

        # Fourth, compute the loss result and update network.
        p_loss = cross_entry(p, target_p)
        v_loss = mse_loss(v, target_v)
        loss = p_loss + args.value_loss_scale * v_loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Accumulate running loss.
        p_running_loss += p_loss.item()
        v_running_loss += v_loss.item()

        # Fifth, dump training verbose.
        if (steps+1) % args.verbose_steps == 0:
            elapsed = time.time() - clock_time
            rate = args.verbose_steps/elapsed
            remaining_steps = max_steps - steps
            estimate_remaining_time = int(remaining_steps/rate)
            print("[{}] steps: {}/{}, {:.2f}% -> policy loss: {:.4f}, value loss: {:.4f} | rate: {:.2f}(steps/sec), estimate: {}(sec)".format(
                      get_currtime(),
                      steps+1,
                      max_steps,
                      100 * ((steps+1)/max_steps),
                      p_running_loss/args.verbose_steps,
                      v_running_loss/args.verbose_steps,
                      rate,
                      estimate_remaining_time))
            running_loss_record.append(
                (steps+1, p_running_loss/args.verbose_steps, v_running_loss/args.verbose_steps))
            p_running_loss = 0
            v_running_loss = 0
            save_checkpoint(network, optimizer, steps+1, args.workspace)
            clock_time = time.time()
        steps += 1

    print("Training is over.");
    if not args.noplot:
        # Sixth plot the running loss graph.
        plot_loss(running_loss_record)
    network.save_pt(get_weights_name("weights"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", metavar="<string>",
                        help="The input SGF files directory. Will use data cache if set None.", type=str)
    parser.add_argument("-s", "--steps", metavar="<integer>",
                        help="Terminate after these steps for each run.", type=int, required=True)
    parser.add_argument("-v", "--verbose-steps", metavar="<integer>",
                        help="Dump verbose and save checkpoint every X steps.", type=int, default=1000)
    parser.add_argument("-b", "--batch-size", metavar="<integer>",
                        help="The batch size number.", type=int, required=True)
    parser.add_argument("-l", "--learning-rate", metavar="<float>",
                        help="The learning rate.", type=float, required=True)
    parser.add_argument("-w", "--workspace", metavar="<string>", default="workspace",
                        help="Will save the checkpoint here.", type=str)
    parser.add_argument("-i", "--imported-games", metavar="<integer>",
                        help="The max number of imported games.", type=int, default=10240000)
    parser.add_argument("--noplot", action="store_true",
                        help="Disable plotting.", default=False)
    parser.add_argument("--lr-decay-steps", metavar="<integer>",
                        help="Reduce the learning rate every X steps.", type=int, default=None)
    parser.add_argument("--lr-decay-factor", metavar="<float>",
                        help="The learning rate decay multiple factor.", type=float, default=0.1)
    parser.add_argument("--value-loss-scale", metavar="<float>",
                        help="Scaling factor of value loss. Default is 0.25 based on AlphaGo paper.", type=float, default=0.25)
    parser.add_argument("--num-workers", metavar="<int>",
                        help="Select a specific number of workerer for DataLoader.", type=int, default=None)

    args = parser.parse_args()
    training_process(args)
