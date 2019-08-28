
import sys
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from .multitau import multitau
from .fftautocorr import fftautocorr
try:
    from .cMultitau import multitau_mt
except ImportError:
    def multitau_mt(signal, lags_per_level=16):
        sys.stderr.write('multithreaded c-extension is missing.')
        sys.stderr.write('falling back to python version')
        return multitau(signal, lags_per_level)
