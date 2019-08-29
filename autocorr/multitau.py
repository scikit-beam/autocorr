import numpy as np


def multitau(signal, lags_per_level=16):
    """Autocorrelation of a signal using multi-tau method.

    For details, please refer to D. Magatti and F. Ferri doi:10.1364/ao.40.004011

    Parameters
    ----------
    signal: 2-D array
        input signal, autocorrlation is calulated along `1-axis`
    lags_per_level: integer, optional
        number of lag-times per level, 16 is a as good number as any other

    Returns:
    --------
    autocorrelations: numpy.ndarray
        should be self-explanatory
    lag-times: numpy.ndarray
        lag times in log2, corresponding to autocorrelation values
    """
    # if N is add subtract 1
    def even(x):
        return x if x % 2 == 0 else x - 1

    # 1-D data hack
    if len(signal.shape) == 1:
        N = even(signal.shape[0])
        a = np.array(signal[np.newaxis, :N], copy=True)
    elif len(signal.shape) == 2:
        # copy data a local array
        N = even(signal.shape[1])
        a = np.array(signal[:, :N], copy=True)
    elif len(signal.shape) > 2:
        raise ValueError('Flatten the [2,3,..] dimensions before passing to autocorrelate.')

    if N < lags_per_level:
        raise ValueError('Lag times per level must be greater than length of signal.')

    #  shorthand for long names
    m = lags_per_level

    # calculate levels
    levels = np.int_(np.log2(N / m)) + 1
    dims = (a.shape[0], (levels + 1) * (m // 2))
    g2 = np.zeros(dims, dtype=np.float32)
    tau = np.zeros(dims[1], dtype=np.float32)

    # zero level
    delta_t = 1
    for i in range(m):
        tau[i] = i * delta_t
        t1 = np.mean(a[:, :N - i], axis=1)
        t2 = np.mean(a[:, i:], axis=1)
        g2[:, i] = np.mean(a[:, :N - i] * a[:, i:], axis=1) / t1 / t2
    a = (a[:, :N:2] + a[:, 1:N:2]) / 2
    N = even(N // 2)

    for level in range(1, levels):
        delta_t *= 2
        for n in range(m // 2):
            idx = m + (level - 1) * (m // 2) + n
            shift = m // 2 + n
            tau[idx] = tau[idx - 1] + delta_t
            t1 = np.mean(a[:, :-shift], axis=1)
            t2 = np.mean(a[:, shift:], axis=1)
            g2[:, idx] = np.mean(a[:, :- shift] * a[:, shift:], axis=1) / t1 / t2
        a = (a[:, :N:2] + a[:, 1:N:2]) / 2
        N = even(N // 2)
        if N < lags_per_level:
            break

    return g2, tau
