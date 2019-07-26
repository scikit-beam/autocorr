#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include "multitau.h"

#include <iostream>

namespace py = pybind11;

#ifdef HAVE_CUDA
extern void cudft(unsigned, float *,  unsigned, float *, complex_t *);
#endif // HAVE_CUDA


py::tuple autocorrelate(py::array_t<float, py::array::c_style | py::array::forcecast> Signal,
				 int m) {

        unsigned nrow = 1, ntimes =0;
        if (Signal.ndim() == 1)
            ntimes = Signal.shape()[0];
		else if (Signal.ndim() == 2) {
		    nrow = Signal.shape()[0];
		    ntimes = Signal.shape()[1];
        }
        else
			throw std::runtime_error("Input signal must be a 1-D or a 2-D numpy array");

		/* get pointer to encapsulated data */
		float * signal = (float *) Signal.request().ptr;

        /* compute the autocorrelations */
        MultiTauAutocorrelator corr(signal, nrow, ntimes);
        corr.process((unsigned) m);

        /* get sizes of from the correlator objest */
        size_t len = corr.length();
        
		/* allocate the buffers for result */
		auto G2  = py::array_t<float>(nrow * len);
		auto Tau = py::array_t<float>(len);

        /* get data-pointers */
		float * g2 = (float *) G2.request().ptr;
        float * tau = (float *) Tau.request().ptr;

        /* copy data */
        std::memcpy(g2, corr.g2(), sizeof(float) * len * nrow);
        std::memcpy(tau, corr.tau(), sizeof(float) * len);

        py::tuple result(2);
        result[0] = G2;
        result[1] = Tau;
        return result;
}

PYBIND11_MODULE (cMultitau, m) {
		m.def("autocorrelate", &autocorrelate, "Same algorithm as python, except uses multiple cores");
}
