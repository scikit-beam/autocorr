import warnings
from ._version import get_versions


from .multitau import multitau
from .fftautocorr import fftautocorr  # noqa
from .cAutocorr import fftautocorr as fftautocorr_mt  # noqa
try:
    from .cAutocorr import multitau_mt
except ImportError:
    def multitau_mt(signal, lags_per_level=16):
        warnings.warn('multithreaded c-extension is missing.', ImportWarning)
        return multitau(signal, lags_per_level)

__version__ = get_versions()['version']
del get_versions
