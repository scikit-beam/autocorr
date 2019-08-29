=====
Usage
=====

Start by importing autocorr.

.. code-block:: python

    import autocorr

Multitau
========

Implementation of multi-tau algorithm for synchrotron XPCS data. For details
refer to **D. Magatti and F. Ferri** *doi:10.1364/ao.40.004011*

Usage
-----

.. code:: python

	import autocorr
	import numpy as np
	import matplotlib.pyplot as plt

	np.random.seed(0)
	signal = np.random.rand(1024, 25, 25)
	signal = signal.reshape(1024, 625)
	G2, tau = autocorr.multitau(signal.T, lags_per_level = 16)
	...
	g2 = G2[roi_mask,:].mean(axis=0)
	plt.semilogx(tau, g2)
	plt.show()
