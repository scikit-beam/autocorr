import numpy as np
import matplotlib.pyplot as plt
import multitau
import time

N = 10240
np.random.seed(0)
t = np.arange(N)
A =  np.exp(-0.05 * t)[:,np.newaxis] + np.random.rand(N, 24) * 0.1

plt.subplot(121)
plt.semilogx(t, A.mean(axis=1))
plt.title('Useless signal')

t0 = time.time()
g1, tau1 = multitau.autocorrelate(A.T, 16)
t1 = time.time()
g2, tau2 = multitau.autocorrelate_mt(A.T, 16)
t2 = time.time()
g3, tau3 = multitau.fftautocorr(A.T)
t3 = time.time()

print('pure python time = %f' % (t1-t0))
print('accelrated version = %f' % (t2-t1))
print('fft version = %f' % (t3-t2))
plt.subplot(122)
plt.semilogx(tau1, g1.mean(axis=0), 'o', label='py')
plt.semilogx(tau2, g2.mean(axis=0), '.', label='c')
plt.semilogx(tau3, g3.mean(axis=0), '.', label='fft')
plt.title('Autocorrelations')
plt.legend()
plt.savefig('autocorr.png')
