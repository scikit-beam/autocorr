#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include "multitau.h"

#include <iostream>

namespace py = pybind11;

#ifdef HAVE_CUDA
extern size_t gpuMultiTau(double *, unsigned, unsigned, unsigned, double *, double *);
#endif // HAVE_CUDA


py::tuple autocorrelate(py::array_t<double, py::array::c_style | py::array::forcecast> Signal,
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
		double * signal = (double *) Signal.request().ptr;

#ifdef HAVE_CUDA
        double * gpu_g2 = nullptr;
        double * gpu_tau = nullptr;
        size_t len = gpuMultiTau(signal, nrow, ntimes, m, gpu_g2, gpu_tau);
#else

        /* compute the autocorrelations */
        MultiTauAutocorrelator corr(signal, nrow, ntimes);
        corr.process((unsigned) m);

        /* get sizes of from the correlator objest */
        size_t len = corr.length();
#endif
        std::vector<ssize_t> shape;
        shape.push_back(nrow);
        shape.push_back(len);
        
		/* allocate the buffers for result */
		auto G2  = py::array_t<double>(shape);
		auto Tau = py::array_t<double>(len);

        /* get data-pointers */
		double * g2 = (double *) G2.request().ptr;
        double * tau = (double *) Tau.request().ptr;

        /* copy data */
#if HAVE_CUDA
        std::memcpy(g2, gpu_g2, sizeof(double) * len * nrow);
        std::memcpy(tau, gpu_tau, sizeof(double) * len);
        delete [] gpu_g2;
        delete [] gpu_tau;
#else // HAVE_CUDA
        std::memcpy(g2, corr.g2(), sizeof(double) * len * nrow);
        std::memcpy(tau, corr.tau(), sizeof(double) * len);
#endif

        py::tuple result(2);
        result[0] = G2;
        result[1] = Tau;
        return result;
}

PYBIND11_MODULE (cMultitau, m) {
		m.def("autocorrelate", &autocorrelate, "Same algorithm as python, except uses multiple cores");
}
