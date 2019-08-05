import numpy as np
import matplotlib.pyplot as plt
import multitau
import time

N = 1024
np.random.seed(0)
t = np.arange(N)
A =  np.exp(-t)[:,np.newaxis] + np.random.rand(N, 24) * 0.1

for i in range(4):
    plt.semilogx(t, A.mean(axis=1))

t0 = time.time()
g1, tau1 = multitau.autocorrelate(A, 16)
t1 = time.time()
g2, tau2 = multitau.autocorrelate_mt(A.T, 16)
t2 = time.time()

print('pure python time = %f' % (t1-t0))
print('accelrated version = %f' % (t2-t1))
plt.figure()
plt.semilogx(tau1, g1.mean(axis=1), 'o', label='py')
plt.semilogx(tau2, g2.mean(axis=0), '.', label='c')
plt.legend()
plt.show()
