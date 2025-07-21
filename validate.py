from network import Network
from config import BOARD_SIZE
from board import NUM_INTESECTIONS

import argparse
import torch
import torch.nn as nn
from train import CACHE_VALID_DIR, DataChopper, Dataset

def report_stats(total, total_samples, correct_policy, total_value_loss):
    policy_acc = correct_policy / total if total > 0 else 0
    value_loss = total_value_loss / total if total > 0 else 0
    print(f"[{total}/{total_samples}] Policy Acc: {100 * policy_acc:.2f}% | Value MSE: {value_loss:.4f}")

@torch.no_grad()
def validate(args):
    # Prepare the validation dataset.
    if args.dir is not None:
        DataChopper(args.dir, args.imported_games)

    dataset = Dataset(CACHE_VALID_DIR)
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=args.batch_size, shuffle=False)

    # Load the model.
    network = Network(BOARD_SIZE)
    network.trainable(False)
    if args.weights is not None:
        network.load_pt(args.weights)
    else:
        raise ValueError("Please specify --weights")

    # Validation loop.
    total = 0
    correct_policy = 0
    total_value_loss = 0.0
    mse_loss = nn.MSELoss()

    total_samples = len(dataset)

    for idx, (inputs, policy, value) in enumerate(dataloader):
        inputs = inputs.to(network.gpu_device)
        policy = policy.to(network.gpu_device)
        value = value.to(network.gpu_device)
        pred_policy, pred_value = network(inputs)
        # policy: take the index of the maximum value
        pred_policy_idx = torch.argmax(pred_policy, dim=1)
        correct_policy += (pred_policy_idx == policy).sum().item()
        # value: MSE
        total_value_loss += mse_loss(pred_value.squeeze(), value.squeeze()).item()
        total += inputs.size(0)

        if idx % 10 == 0:
            report_stats(total, total_samples, correct_policy, total_value_loss)
    report_stats(total, total_samples, correct_policy, total_value_loss)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", metavar="<string>",
                        help="The input SGF files directory. Will use data cache if set None.", type=str, default=None)
    parser.add_argument("-w", "--weights", metavar="<string>",
                        help="The weights file name.", type=str, required=True)
    parser.add_argument("-b", "--batch-size", metavar="<integer>",
                        help="The batch size number.", type=int, default=256)
    parser.add_argument("-i", "--imported-games", metavar="<integer>",
                        help="The max number of imported games.", type=int, default=10240000)
    args = parser.parse_args()
    validate(args)
