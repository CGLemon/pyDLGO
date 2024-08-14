from network import Network
from config import BOARD_SIZE
import argparse
import torch
import time

def load_checkpoint(network, checkpoint):
    state_dict = torch.load(checkpoint, map_location=network.gpu_device)
    network.load_state_dict(state_dict["network"])
    return network

def get_currtime():
    lt = time.localtime(time.time())
    return "{y}-{m}-{d}-{h:02d}-{mi:02d}-{s:02d}".format(
                y=lt.tm_year, m=lt.tm_mon,  d=lt.tm_mday, h=lt.tm_hour, mi=lt.tm_min, s=lt.tm_sec)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--checkpoint", metavar="<string>",
                        help="The inpute checkpoint file name.", type=str)
    args = parser.parse_args()

    if args.checkpoint:
        network = Network(BOARD_SIZE, use_gpu=False)
        network = load_checkpoint(network, args.checkpoint)
        network.save_pt("weights-{}.pt".format(get_currtime()))
