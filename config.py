BOARD_SIZE = 9 # The default and max board size. We can reset the value later.

KOMI = 7 # The default komi. We can reset the value later.

USE_GPU = True # Set true will use the GPU automatically if you have one.

BLOCK_SIZE = 2 # The network residual block size.

BLOCK_CHANNELS = 64 # The number of network residual channels.

POLICY_CHANNELS = 8 # The number of value head channels.

VALUE_CHANNELS = 4 # The number of policy head channels.

INPUT_CHANNELS = 18 # Number of the network input layers.

PAST_MOVES = 8 # Number of past moves encoding to the planes.

USE_SE = False # Enable Squeeze-and-Excite net struct.

USE_POLICY_ATTENTION = False # Enable self-attention net struct.
