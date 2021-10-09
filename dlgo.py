#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gtp import GTP_LOOP
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--playouts", metavar="<integer>",
                        help="The number of playouts", type=int, default=400)
    parser.add_argument("-w", "--weights", metavar="<string>",
                        help="The weights file name", type=str)
    parser.add_argument("-r", "--resign-threshold", metavar="<float>",
                        help="Resign when winrate is less than x.", type=float, default=0.1)
    parser.add_argument("-v", "--verbose",
                        help="Dump some search verbose", action="store_true")
    parser.add_argument("-k", "--kgs",
                        help="Dump some hit verbose on KGS.", action="store_true")

    args = parser.parse_args()
    loop = GTP_LOOP(args)
