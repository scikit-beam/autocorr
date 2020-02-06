import numpy as np
from numpy.testing import assert_array_equal
import autocorr
import time

N = 10240
np.random.seed(0)
t = np.arange(N)
A = np.exp(-0.05 * t)[:, np.newaxis] + np.random.rand(N, 24) * 0.1
original = A.copy()


def test_multitau():
    t0 = time.time()
    g1, tau = autocorr.multitau(A.T, 16)
    t1 = time.time()
    # Check that the input array has not been mutated.
    assert_array_equal(A, original)
    print('pure python time = %f' % (t1 - t0))


def test_multitau_mt():
    t0 = time.time()
    g1, tau = autocorr.multitau_mt(A.T, 16)
    t1 = time.time()
    # Check that the input array has not been mutated.
    assert_array_equal(A, original)
    print('accelerated version = %f' % (t1 - t0))


def test_fftautocorr():
    t0 = time.time()
    g2, tau = autocorr.fftautocorr(A.T)
    t1 = time.time()
    # Check that the input array has not been mutated.
    assert_array_equal(A, original)
    print('fft version = %f' % (t1 - t0))


def test_cfftautocorr():
    t0 = time.time()
    g2, tau = autocorr.fftautocorr_mt(A.T)
    t1 = time.time()
    # Check that the input array has not been mutated.
    assert_array_equal(A, original)
    print('fft version = %f' % (t1 - t0))
