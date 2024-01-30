# Simple Usage

## Requirements
1. PyTorch (1.x version)
2. NumPy
3. Tkinter
4. Matplotlib

## Open With Built-in GUI

You may download the pre-training model from release section named 預先訓練好的小型權重. Then put the pt file to the dlgo directory and enter following command. 

    $ python3 dlgo.py --weights nn_2x64.pt --gui

The dlgo will use your GPU automatically. If you want to disable GPU, set the value ```USE_GPU``` False.


## Open With GTP GUI

The dlgo support the GTP GUI. [Sabaki](https://sabaki.yichuanshen.de) is recommanded. Some helpful optional arguments are here.

    optional arguments:
      -p <integer>, --playouts <integer>
                            The number of playouts.
      -w <string>, --weights <string>
                            The weights file name.
      -r <float>, --resign-threshold <float>
                            Resign when winrate is less than x.

The sample command is here.

    $ dlgo.py --weights nn_2x64.pt -p 1600 -r 0.25

## Training

Following above simple steps to train a new weights

1. Preparing the sgf files. You may just use the sgf.zip. The zip including around 35000 9x9 games.
2. Set the network parametes in the config.py. Including ```BOARD_SIZE```, ```BLOCK_SIZE```, ```FILTER_SIZE```.
3. Start training.

        $ python3 train.py --dir sgf-directory-name --steps 128000 --batch-size 512 --learning-rate 0.005 --weights-name weights

Some helpful arguments are here.

    optional arguments:
      -h, --help            show this help message and exit
      -d <string>, --dir <string>
                            The input SGF files directory. Will use data cache if set None.
      -s <integer>, --steps <integer>
                            Terminate after these steps.
      -v <integer>, --verbose-steps <integer>
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
