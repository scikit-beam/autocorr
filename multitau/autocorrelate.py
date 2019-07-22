#! /usr/bin/env python

import numpy as np

def autocorrelate(signal, lag_times=16, normalization='default'):
    """Autocorrelation of a signal using multi-tau method.

    For details, please refer to D. Magatti and F. Ferri doi:10.1364/ao.40.004011
    
    Parameters
    ----------
    signal: array
        input signal, corrlation is calulated along `0-axis`
    lag_times: integer, optional
        number of lag-times per level, 16 is a as good number as any other
    normalization: str, optional
        default: :math: `\\frac { \langle f(t) f(t - \\tau) \\rangle }{ \langle f(t) \\rangle^2 }`
        sutton: :math: `\\frac { \langle f(t) f(t - \\tau) \\rangle }{ \langle f(t) \\rangle \langle f(t - \\tau) \\rangle }`

    Returns:
    --------
    autocorrelations: numpy.ndarray
        should be self-explanatory
    lag-times: numpy.ndarray
        lag times in log2, corresponding to autocorrelation values     

    TODO: add sanity checks
    """
    even = lambda x : x if x % 2 == 0 else x - 1
    N = even(signal.shape[0])
    a = np.array(signal[:N], copy=True)
    m = lag_times

    # calculate levels
    levels = np.int_(np.log2(N/m)) + 1
    dims = ((levels + 1) * (m //2), *a.shape[1:])
    g2 = np.zeros(dims, dtype=np.float32)
    tau = np.zeros_like(g2)

    # zero level
    delta_t = 1
    for i in range(m):
        tau[i] = i * delta_t
        t1 = np.mean(a[:N-i], axis=0) 
        t2 = np.mean(a[i:], axis=0) 
        if normalization == 'default':
            g2[i] = np.mean(a[:N-i] * a[i:], axis=0) /t1/t1
        else:
            g2[i] = np.mean(a[:N-i] * a[i:], axis=0) /t1/t2
    a  = (a[:N:2] + a[1:N:2])/2
    N  = even(N//2)

    for level in range(1, levels):
        delta_t *= 2
        for n in range(m//2):
            idx = m + (level-1) * (m//2) + n
            shift = m//2 + n
            tau[idx] = tau[idx-1] + delta_t
            t1 = np.mean(a[:-shift], axis=0)
            t2 = np.mean(a[shift:], axis=0)
            if normalization == 'default':
                g2[idx] = np.mean(a[:-shift] * a[shift:], axis=0)/t1/t1
            else:
                g2[idx] = np.mean(a[:-shift] * a[shift:], axis=0)/t1/t2
        a  = (a[:N:2] + a[1:N:2])/2
        N = even(N//2)
        if N < lag_times: break 

    return g2, tau
