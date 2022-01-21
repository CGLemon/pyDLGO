# Simple Usage

## Requirements
1. PyTorch (1.x version)
2. NumPy
3. Tkinter
4. Matplotlib


## Open With Built-in CUI

You may download the pre-training model from release section named 預先訓練好的小型權重. Then put the pt file to the dlgo directory and enter following commands. 

    $ python3 dlgo.py --weights nn_2x64.pt --gui


## Open with GTP Interface

The dlgo support for the GTP GUI. [Sabaki](https://sabaki.yichuanshen.de) is recommanded. Some helpful optional arguments are here.

    optional arguments:
      -p <integer>, --playouts <integer>
                            The number of playouts
      -w <string>, --weights <string>
                            The weights file name
      -r <float>, --resign-threshold <float>
                            Resign when winrate is less than x.


## Training

Some simple steps to train a new weights

1. Preparing the sgf files. You may just use the sgf.zip. The zip including 35000 9x9 games.
2. Set the network parametes in the config.py. Including BOARD_SIZE, BLOCK_SIZE, FILTER_SIZE.
3. Start training.

        $ python3 train.py --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights

Some helpful optional arguments are here.

    optional arguments:
      -d <string>, --dir <string>
                            The input directory
      -s <integer>, --step <integer>
                            The training step
      -v <integer>, --verbose-step <integer>
                            Dump verbose on every X steps.
      -b <integer>, --batch-size <integer>
                            The batch size number.
      -l <float>, --learning-rate <float>
                            The learning rate.
      -w <string>, --weights-name <string>
                            The output weights name.
      --load-weights <string>
                            The inputs weights name.
      --noplot              Disable plotting.
