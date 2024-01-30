import torch
import torch.nn as nn
import torch.nn.functional as F

from config import *
from transformer import TransformerEncoderOnly 

class FullyConnect(nn.Module):
    def __init__(self, in_size,
                       out_size,
                       relu=True):
        super().__init__()
        self.relu = relu
        self.linear = nn.Linear(in_size, out_size)

    def forward(self, x):
        x = self.linear(x)
        return F.relu(x, inplace=True) if self.relu else x

class ConvBlock(nn.Module):
    def __init__(self, in_channels,
                       out_channels,
                       kernel_size,
                       relu=True):
        super().__init__()
 
        assert kernel_size in (1, 3)
        self.relu = relu
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            padding="same",
            bias=True,
        )
        self.bn = nn.BatchNorm2d(
            out_channels,
            eps=1e-5
        )

        nn.init.kaiming_normal_(self.conv.weight,
                                mode="fan_out",
                                nonlinearity="relu")
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return F.relu(x, inplace=True) if self.relu else x

class ResBlock(nn.Module):
    def __init__(self, channels, se_size=None):
        super().__init__()
        self.with_se=False
        self.channels=channels

        self.conv1 = ConvBlock(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3
        )
        self.conv2 = ConvBlock(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            relu=False
        )

        if se_size != None:
            self.with_se = True
            self.avg_pool = nn.AdaptiveAvgPool2d(1)
            self.squeeze = FullyConnect(
                in_size=channels,
                out_size=se_size,
                relu=True
            )
            self.excite = FullyConnect(
                in_size=se_size,
                out_size=2 * channels,
                relu=False
            )

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)
        
        if self.with_se:
            b, c, _, _ = out.size()
            seprocess = self.avg_pool(out)
            seprocess = torch.flatten(seprocess, start_dim=1, end_dim=3)
            seprocess = self.squeeze(seprocess)
            seprocess = self.excite(seprocess)

            gammas, betas = torch.split(seprocess, self.channels, dim=1)
            gammas = torch.reshape(gammas, (b, c, 1, 1))
            betas = torch.reshape(betas, (b, c, 1, 1))
            out = torch.sigmoid(gammas) * out + betas
            
        out += identity

        return F.relu(out, inplace=True)


class Network(nn.Module):
    def __init__(self, board_size,
                       input_channels=INPUT_CHANNELS,
                       block_size=BLOCK_SIZE,
                       block_channels=BLOCK_CHANNELS,
                       policy_channels=POLICY_CHANNELS,
                       value_channels=VALUE_CHANNELS,
                       use_se=USE_SE,
                       use_policy_attention=USE_POLICY_ATTENTION,
                       use_gpu=USE_GPU):
        super().__init__()

        self.nn_cache = {}

        self.block_size = block_size
        self.residual_channels = block_channels
        self.policy_channels = policy_channels
        self.value_channels = value_channels
        self.value_layers = 256
        self.board_size = board_size
        self.spatial_size = self.board_size ** 2
        self.input_channels = input_channels
        self.use_se = use_se
        self.use_policy_attention = use_policy_attention
        self.use_gpu = True if torch.cuda.is_available() and use_gpu else False
        self.gpu_device = torch.device('cpu')

        if self.use_se:
            assert self.residual_channels // 2 == 0, "BLOCK_CHANNELS must be divided by 2."

        self.construct_layers()
        if self.use_gpu:
            self.gpu_device = torch.device('cuda')
            self.to_gpu_device()

    def to_gpu_device(self):
        self = self.to(self.gpu_device)

    def construct_layers(self):
        self.input_conv = ConvBlock(
            in_channels=self.input_channels,
            out_channels=self.residual_channels,
            kernel_size=3,
            relu=True
        )

        # residual tower
        nn_stack = []
        for s in range(self.block_size):
            se_size = None
            if self.use_se:
                se_size = self.residual_channels // 2
            nn_stack.append(ResBlock(self.residual_channels, se_size))

        self.residual_tower = nn.Sequential(*nn_stack)

        # policy head
        if self.use_policy_attention:
            self.encoder_layers = TransformerEncoderOnly(
                d_model=self.residual_channels,
                n_head=4,
                dim_feedforward=2*self.residual_channels,
                num_layer=1,
                drop_rate=0
            )

        self.policy_conv = ConvBlock(
            in_channels=self.residual_channels,
            out_channels=self.policy_channels,
            kernel_size=1,
            relu=True
        )
        self.policy_fc = FullyConnect(
            in_size=self.policy_channels * self.spatial_size,
            out_size=self.spatial_size + 1,
            relu=False
        )

        # value head
        self.value_conv = ConvBlock(
            in_channels=self.residual_channels,
            out_channels=self.value_channels,
            kernel_size=1,
            relu=True
        )

        self.value_fc = FullyConnect(
            in_size=self.value_channels * self.spatial_size,
            out_size=self.value_layers,
            relu=True
        )
        self.winrate_fc = FullyConnect(
            in_size=self.value_layers,
            out_size=1,
            relu=False
        )

    def forward(self, planes):
        x = self.input_conv(planes)

        # residual tower
        x = self.residual_tower(x)

        # policy head
        pol = x

        if self.use_policy_attention:
            n, c, h, w = pol.size()

            pol = torch.reshape(pol, (n, c, h*w))
            pol = pol.transpose(1,2)

            pol = self.encoder_layers(pol)

            pol = pol.transpose(1,2)
            pol = torch.reshape(pol, (n, c, h, w))

        pol = self.policy_conv(pol)
        pol = self.policy_fc(torch.flatten(pol, start_dim=1, end_dim=3))

        # value head
        val = self.value_conv(x)
        val = self.value_fc(torch.flatten(val, start_dim=1, end_dim=3))
        val = self.winrate_fc(val)

        return pol, torch.tanh(val)
        
    def get_outputs(self, planes):
        # TODO: Limit the NN cache size.

        h = hash(planes.tostring())
        res = self.nn_cache.get(h) # search the NN computation

        if res is not None:
            p, v = res
            return p, v

        m = nn.Softmax(dim=1)
        x = torch.unsqueeze(torch.tensor(planes, dtype=torch.float32), dim=0)
        if self.use_gpu:
            x = x.to(self.gpu_device)
        p, v = self.forward(x)
        p, v = m(p).data.tolist()[0], v.data.tolist()[0]

        self.nn_cache[h] = (p, v) # save the NN computation

        return p, v

    def clear_cache(self):
        self.nn_cache.clear()

    def trainable(self, t=True):
        torch.set_grad_enabled(t)
        if t==True:
            self.train()
        else:
            self.eval()

    def save_pt(self, filename):
        torch.save(self.state_dict(), filename)

    def load_pt(self, filename):
        self.load_state_dict(torch.load(filename, map_location=self.gpu_device))
