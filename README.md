# Multitau
Implementation of multi-tau algorithm for synchrotron XPCS data. For details refer to **D. Magatti and F. Ferri** *doi:10.1364/ao.40.004011*

## Installation
```bash
git clone https://github.com/aryabhatt/multitau.git
python setup.py install
```
### Requirements
1. numpy
2. cmake
3. pybind11

## Usage
```python
import multitau
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
signal = np.random.rand(1024, 25, 25)
signal = signal.reshape(1024, 625)
G2, tau = multitau.autocorrelate(signal.T, lags_per_level = 16)
...
g2 = G2[roi_mask,:].mean(axis=0)
plt.semilogx(tau, g2)
plt.show()
```
```idx``` could be a mask for ROIs.
