
import sys
import warnings
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from .multitau import multitau
from .fftautocorr import fftautocorr
try:
    from .cMultitau import multitau_mt
except ImportError:
    def multitau_mt(signal, lags_per_level=16):
        warnings.warn('multithreaded c-extension is missing.', ImportWarning)
        return multitau(signal, lags_per_level)
