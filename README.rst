===============================
autocorr
===============================

.. image:: https://img.shields.io/travis/scikit-beam/autocorr.svg
        :target: https://travis-ci.org/scikit-beam/autocorr

.. image:: https://img.shields.io/pypi/v/autocorr.svg
        :target: https://pypi.python.org/pypi/autocorr


This library, still in very early development, aims to grow into a one-stop
shop for all things XPCS. As it first step, it will be used to study and
consolidate many existing implementations of g2 autocorrelation and related
functions.

Multitau
--------
Implementation of multi-tau algorithm for synchrotron XPCS data. For details refer to **D. Magatti and F. Ferri** *doi:10.1364/ao.40.004011*


Requirements
------------
1. numpy
2. pybind11

Usage
-----

.. code-block :: python
	

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