from network import Network
from config import BOARD_SIZE
from train import get_weights_name
import argparse
import torch
import time

def load_checkpoint(network, checkpoint):
    state_dict = torch.load(checkpoint, map_location=network.gpu_device, weights_only=True)
    network.load_state_dict(state_dict["network"])
    return network

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--checkpoint", metavar="<string>",
                        help="The inpute checkpoint file name.", type=str)
    args = parser.parse_args()

    if args.checkpoint:
        network = Network(BOARD_SIZE, use_gpu=False)
        network = load_checkpoint(network, args.checkpoint)
        network.save_pt(get_weights_name("weights"))
    else:
        print("Please give the checkpoint path.")
