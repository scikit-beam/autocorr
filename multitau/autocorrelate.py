#! /usr/bin/env python

import numpy as np

def autocorrelate(signal, lag_times=16, normalization='default', 
                  roi_labels=None, labeled_roi_mask=None):
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
    labels: list
        list of labels in the labled ROI array
    labeled_roi_mask: array
        array with ROI lables    

    Returns:
    --------
    autocorrelations: numpy.ndarray
        should be self-explanatory
    lag-times: numpy.ndarray
        lag times in log2, corresponding to autocorrelation values     

    TODO: add sanity checks
    """
    # if N is add subtract 1
    even = lambda x : x if x % 2 == 0 else x - 1

    # prep signal array
    N = even(signal.shape[0])
    m = lag_times

    # copy data a local array
    a = np.array(signal[:N], copy=True)

    # use mask if using ROIs
    if roi_labels is not None:
        a = a[:, labeled_roi_mask > 0]
    else: 
        # flattn the image
        _, row, col = a.shape
        a = a.reshape(N, row * col)

    # transpose signal so that time is the fastest moving index
    a = np.transpose(a)

    # calculate levels
    levels = np.int_(np.log2(N/m)) + 1
    dims = ((levels + 1) * (m //2), a.shape[0])
    g2 = np.zeros(dims, dtype=np.float32)
    tau = np.zeros(dims[0], dtype=np.float32)

    # zero level
    delta_t = 1
    for i in range(m):
        tau[i] = i * delta_t
        t1 = np.mean(a[:,:N-i], axis=1) 
        t2 = np.mean(a[:,i:], axis=1) 
        if normalization == 'default':
            g2[i,:] = np.mean(a[:,:N-i] * a[:,i:], axis=1) /t1/t1
        else:
            g2[i,:] = np.mean(a[:,:N-i] * a[:,i:], axis=1) /t1/t2
    a  = (a[:,:N:2] + a[:,1:N:2])/2
    N  = even(N//2)

    for level in range(1, levels):
        delta_t *= 2
        for n in range(m//2):
            idx = m + (level-1) * (m//2) + n
            shift = m//2 + n
            tau[idx] = tau[idx-1] + delta_t
            t1 = np.mean(a[:,:-shift], axis=1)
            t2 = np.mean(a[:,shift:], axis=1)
            if normalization == 'default':
                g2[idx,:] = np.mean(a[:,:-shift] * a[:,shift:], axis=1)/t1/t1
            else:
                g2[idx,:] = np.mean(a[:,:-shift] * a[:,shift:], axis=1)/t1/t2
        a  = (a[:,:N:2] + a[:,1:N:2])/2
        N = even(N//2)
        if N < lag_times: break 

    G2 = []
    if roi_labels is None:
        G2.append(g2.mean(axis=1))
    else:
        for label in roi_labels:
            mask = labeled_roi_mask > 0
            idxs = labeled_roi_mask[mask] == label
            G2.append(g2[:,idxs].mean(axis=1))
    return G2, tau
