import torch
import torch.nn as nn
import torch.nn.functional as F

from config import INPUT_CHANNELS, BLOCK_SIZE, FILTER_SIZE, USE_GPU

class FullyConnect(nn.Module):
    def __init__(self, in_size,
                       out_size,
                       relu=True,
                       collector=None):
        super().__init__()
        self.relu = relu
        self.linear = nn.Linear(in_size, out_size)

        if collector != None:
            collector.append(self.linear.weight)
            collector.append(self.linear.bias)

    def forward(self, x):
        x = self.linear(x)
        return F.relu(x, inplace=True) if self.relu else x

class ConvBlock(nn.Module):
    def __init__(self, in_channels,
                       out_channels,
                       kernel_size,
                       relu=True,
                       collector=None):
        super().__init__()
 
        assert kernel_size in (1, 3)
        self.relu = relu
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            padding=1 if kernel_size == 3 else 0,
            bias=True,
        )
        self.bn = nn.BatchNorm2d(
            out_channels,
            eps=1e-5
        )

        if collector != None:
            collector.append(self.conv.weight)
            collector.append(self.conv.bias)
            collector.append(self.bn.weight)
            collector.append(self.bn.bias)
            collector.append(self.bn.running_mean)
            collector.append(self.bn.running_var)

        nn.init.kaiming_normal_(self.conv.weight,
                                mode="fan_out",
                                nonlinearity="relu")
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return F.relu(x, inplace=True) if self.relu else x

class ResBlock(nn.Module):
    def __init__(self, channels, se_size=None, collector=None):
        super().__init__()
        self.with_se=False
        self.channels=channels

        self.conv1 = ConvBlock(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            collector=collector
        )
        self.conv2 = ConvBlock(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            relu=False,
            collector=collector
        )

        if se_size != None:
            self.with_se = True
            self.avg_pool = nn.AdaptiveAvgPool2d(1)
            self.extend = FullyConnect(
                in_size=channels,
                out_size=se_size,
                relu=True,
                collector=collector
            )
            self.squeeze = FullyConnect(
                in_size=se_size,
                out_size=2 * channels,
                relu=False,
                collector=collector
            )

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)
        
        if self.with_se:
            b, c, _, _ = out.size()
            seprocess = self.avg_pool(out)
            seprocess = torch.flatten(seprocess, start_dim=1, end_dim=3)
            seprocess = self.extend(seprocess)
            seprocess = self.squeeze(seprocess)

            gammas, betas = torch.split(seprocess, self.channels, dim=1)
            gammas = torch.reshape(gammas, (b, c, 1, 1))
            betas = torch.reshape(betas, (b, c, 1, 1))
            out = torch.sigmoid(gammas) * out + betas
            
        out += identity

        return F.relu(out, inplace=True)


class Network(nn.Module):
    def __init__(self, board_size,
                       input_channels=INPUT_CHANNELS,
                       block_size = BLOCK_SIZE,
                       filter_size = FILTER_SIZE,
                       use_gpu=USE_GPU):
        super().__init__()

        self.nn_cache = {}

        self.tensor_collector = []
        self.block_size = block_size
        self.residual_channels = filter_size
        self.policy_channels = 8
        self.value_channels = 4
        self.value_layers = 256
        self.board_size = board_size
        self.spatial_size = self.board_size ** 2
        self.input_channels = input_channels
        self.use_gpu = True if torch.cuda.is_available() and use_gpu else False
        self.gpu_device = torch.device('cpu')

        self.set_layers()
        if self.use_gpu:
            self.gpu_device = torch.device('cuda')
            self.to_gpu_device()

    def to_gpu_device(self):
        self = self.to(self.gpu_device)

    def set_layers(self):
        self.input_conv = ConvBlock(
            in_channels=self.input_channels,
            out_channels=self.residual_channels,
            kernel_size=3,
            relu=True,
            collector=self.tensor_collector
        )

        # residual tower
        nn_stack = []
        for s in range(self.block_size):
            nn_stack.append(ResBlock(self.residual_channels,
                                     None,
                                     self.tensor_collector))
        self.residual_tower = nn.Sequential(*nn_stack)

        # policy head
        self.policy_conv = ConvBlock(
            in_channels=self.residual_channels,
            out_channels=self.policy_channels,
            kernel_size=1,
            relu=True,
            collector=self.tensor_collector
        )
        self.policy_fc = FullyConnect(
            in_size=self.policy_channels * self.spatial_size,
            out_size=self.spatial_size + 1,
            relu=False,
            collector=self.tensor_collector
        )

        # value head
        self.value_conv = ConvBlock(
            in_channels=self.residual_channels,
            out_channels=self.value_channels,
            kernel_size=1,
            relu=True,
            collector=self.tensor_collector
        )

        self.value_fc = FullyConnect(
            in_size=self.value_channels * self.spatial_size,
            out_size=self.value_layers,
            relu=True,
            collector=self.tensor_collector
        )
        self.winrate_fc = FullyConnect(
            in_size=self.value_layers,
            out_size=1,
            relu=False,
            collector=self.tensor_collector
        )

    def forward(self, planes):
        x = self.input_conv(planes)

        # residual tower
        x = self.residual_tower(x)

        # policy head
        pol = self.policy_conv(x)
        pol = self.policy_fc(torch.flatten(pol, start_dim=1, end_dim=3))

        # value head
        val = self.value_conv(x)
        val = self.value_fc(torch.flatten(val, start_dim=1, end_dim=3))
        val = self.winrate_fc(val)

        return pol, torch.tanh(val)
        
    def get_outputs(self, planes):
        # TODO: Limit the nn cache size.

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
