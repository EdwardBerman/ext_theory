# This repo contains code for the ICML submission "A General Theory on Correct, Incorrect, and Extrinsic Equivariance"

## Requirements
1. Install PyTorch (recommended 1.10.2)
1. `pip install -r requirements.txt`

## Swiss Roll Experiment
```
cd spiral
python main.py --model=dssz // invariant network
python main.py --model=mlp // unconstained network
```

## Square Experiment
```
cd square
python main.py 
```

## Regression Experiment
```
cd regression
python main.py
```