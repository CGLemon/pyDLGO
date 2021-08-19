#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gtp import GTP_LOOP
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--playouts", help="The number of playouts", type=int)
    parser.add_argument("-w", "--weights", help="The weights file name", type=int)

    args = parser.parse_args()
    loop = GTP_LOOP(args)
