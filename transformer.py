import math
import numpy as np
import torch
import torch.nn as nn
from torch.nn import functional as F

# ref: https://github.com/pytorch/pytorch/blob/master/torch/nn/modules/transformer.py

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model,
                       n_head,
                       drop_rate):
        super().__init__()
        assert d_model % n_head == 0

        self.d_mode = d_model
        self.n_head = n_head

        # key, query, value projections for all heads
        self.key_proj = nn.Linear(d_model, d_model)
        self.query_proj = nn.Linear(d_model, d_model)
        self.value_proj = nn.Linear(d_model, d_model)

        # dropout layer
        self.drop = nn.Dropout(drop_rate)
        
        # output projection
        self.proj = nn.Linear(d_model, d_model)

    def split_heads(self, x):
        N, T, D = x.size() # batch size, sequence length, model dimensionality
        x = torch.reshape(x,(N, T, self.n_head, D // self.n_head))
        return x.transpose(1, 2)

    def forward(self, q, k, v, mask):
        # k, q, v: (N, T, nh * hs)

        k = self.split_heads(self.key_proj(k))   # (N, nh, T, hs)
        q = self.split_heads(self.value_proj(q)) # (N, nh, T, hs)
        v = self.split_heads(self.query_proj(v)) # (N, nh, T, hs)

        # causal self-attention; Self-attend: (N, nh, T, hs) x (N, nh, hs, T) -> (N, nh, T, T)
        att = torch.matmul(q, k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))

        if mask is not None:
            # mask fliters unused attention value
            _,_,T_k, T_q = att.size()
            att = att.masked_fill(mask[:,:,:T_k,:T_q] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)

        context = torch.matmul(att, v) # (N, nh, T, T) x (N, nh, T, hs) -> (N, nh, T, hs)
        context = context.transpose(1, 2)  # (N, T, nh, hs)
        context = context.reshape((context.shape[0], context.shape[1],-1))  # (N, T, nh * hs)
        context = self.drop(self.proj(context))

        return context

class FeedForward(nn.Module):
    def __init__(self, d_model,
                       dim_feedforward,
                       drop_rate):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.GELU(),
            nn.Dropout(drop_rate),
            nn.Linear(dim_feedforward, d_model),
            nn.Dropout(drop_rate)
        )
    def forward(self, x):
        return self.net(x)

class EncoderLayer(nn.Module):
    def __init__(self, d_model,
                       n_head,
                       dim_feedforward,
                       drop_rate):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.mha = MultiHeadAttention(d_model, n_head, drop_rate)
        self.ff = FeedForward(d_model, dim_feedforward, drop_rate)

    def forward(self, x, mask):
        x = self.norm1(x)
        x = x + self.mha(x,x,x,mask)

        x = self.norm2(x)
        x = x + self.ff(x)
        return x

class Encoder(nn.Module):
    def __init__(self, n_head,
                       d_model,
                       dim_feedforward,
                       n_layer,
                       drop_rate):
        super().__init__()

        self.n_layer = n_layer
        self.layers = nn.ModuleList(
            [EncoderLayer(d_model, n_head, dim_feedforward, drop_rate) for _ in range(n_layer)]
        )
    
    def forward(self, x, mask):
        for encoder in self.layers:
            x = encoder(x, mask)
        return x

class DecoderLayer(nn.Module):
    def __init__(self, d_model,
                       n_head,
                       dim_feedforward,
                       drop_rate):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)

        self.sa = MultiHeadAttention(d_model, n_head, drop_rate)
        self.mha = MultiHeadAttention(d_model, n_head, drop_rate)
        self.ff = FeedForward(d_model, dim_feedforward, drop_rate)

    def forward(self, x, y, x_mask, y_mask):
        x = self.norm1(x)
        x = x + self.sa(x,x,x,x_mask)

        x = self.norm2(x)
        x = x + self.mha(x,y,y,y_mask)

        x = self.norm3(x)
        x = x + self.ff(x)
        return x

class Decoder(nn.Module):
    def __init__(self, n_head,
                       d_model,
                       dim_feedforward,
                       n_layer,
                       drop_rate):
        super().__init__()

        self.n_layer = n_layer
        self.layers = nn.ModuleList(
            [DecoderLayer(d_model, n_head, dim_feedforward, drop_rate) for _ in range(n_layer)]
        )
    
    def forward(self, x, y, x_mask, y_mask):
        for decoder in self.layers:
            x = decoder(x, y, x_mask, y_mask)
        return x

class Transformer(nn.Module):
    def __init__(self, d_model=512,
                       n_head = 8,
                       dim_feedforward=2048,
                       num_encoder_layer=6,
                       num_decoder_layer=6,
                       drop_rate=0.1):
        super().__init__()

        self.encoder = Encoder(n_head, d_model, dim_feedforward, num_encoder_layer, drop_rate)
        self.decoder = Decoder(n_head, d_model, dim_feedforward, num_decoder_layer, drop_rate)

    def forward(self, src, tgt, src_mask=None, tgt_mask=None, ecd_mask=None):
        encoded = self.encoder(src, src_mask)
        decoded = self.decoder(tgt, encoded, tgt_mask, ecd_mask)
        return decoded

class TransformerEncoderOnly(nn.Module):
    def __init__(self, d_model=512,
                       n_head=8,
                       dim_feedforward=2048,
                       num_layer=6,
                       drop_rate=0.1):
        super().__init__()

        self.encoder = Encoder(n_head, d_model, dim_feedforward, num_layer, drop_rate)

    def forward(self, x, mask=None):
        x = self.encoder(x, mask)
        return x

if __name__ == '__main__':
    src = torch.rand(1, 10, 512)
    tgt = torch.rand(1, 10, 512)

    transformer = Transformer(d_model=512)
    transformer.eval()
    o0 = transformer(src, tgt)
    print(o0.size()) # should be [1, 10, 512]

    gpt = TransformerEncoderOnly(d_model=512)
    gpt.eval()
    o1 = gpt(src)
    print(o1.size()) # should be [1, 10, 512]
