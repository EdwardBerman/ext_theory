import numpy as np
import torch
import argparse
import os

def strToBool(value):
    if value.lower() in {'false', 'f', '0', 'no', 'n'}:
        return False
    elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    raise ValueError(f'{value} is not a valid boolean value')

def noneOrStr(value):
    if value == 'None':
        return None
    return value

current_directory = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(current_directory, 'output')

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='mlp')
parser.add_argument('--seed', type=int, default=0)
parser.add_argument('--device', type=str, default='cuda:1')
parser.add_argument('--cr', type=float, default=0.)
parser.add_argument('--icr', type=float, default=0.)
parser.add_argument('--n_data', type=int, default=200)
parser.add_argument('--log_pre', type=str, default=output_directory)

args = parser.parse_args()
model = args.model
seed = args.seed
device = args.device
cr = args.cr
icr = args.icr
n_data = args.n_data
log_pre = args.log_pre
