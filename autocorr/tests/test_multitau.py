import numpy as np
import autocorr
import time

N = 10240
np.random.seed(0)
t = np.arange(N)
A = np.exp(-0.05 * t)[:, np.newaxis] + np.random.rand(N, 24) * 0.1


def test_multitau():
    t0 = time.time()
    g1, tau1 = autocorr.multitau(A.T, 16)
    t1 = time.time()
    print('pure python time = %f' % (t1 - t0))


def test_multitau_mt():
    t0 = time.time()
    g1, tau1 = autocorr.multitau_mt(A.T, 16)
    t1 = time.time()
    print('accelerated version = %f' % (t1 - t0))


def test_fftautocorr():
    t0 = time.time()
    g3, tau3 = autocorr.fftautocorr(A.T)
    t1 = time.time()
    print('fft version = %f' % (t1 - t0))
