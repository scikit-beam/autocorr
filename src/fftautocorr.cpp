
#include <fftw3.h>
#include <omp.h>
#include <iostream>

#include "autocorr.h"

inline void abs(fftw_complex & x){
    x[0] = x[0] * x[0] + x[1] * x[1];
    x[1] = 0.f;
}

void fft(double *& input, fftw_complex *& output,  int len, int batches) {

    int rank = 1;
    int n[] = { len };
    int idist = len;
    int odist = len/2+1;
    int istride = 1;
    int ostride = 1;
    int *inembed = NULL;
    int *onembed = NULL;
    fftw_plan plan = fftw_plan_many_dft_r2c(rank, n, batches, input, inembed,
        istride, idist, output, onembed, ostride, odist, FFTW_ESTIMATE);
    fftw_execute(plan);
    fftw_destroy_plan(plan);
}

void ifft(fftw_complex *& input, double *& output, int len, int batches) {
    int rank = 1;
    int n[] = { len };
    int idist = len/2+1;
    int odist = len;
    int istride = 1;
    int ostride = 1;
    int *inembed = NULL;
    int *onembed = NULL;
    fftw_plan plan = fftw_plan_many_dft_c2r(rank, n, batches, input, inembed,
        istride, idist, output, onembed, ostride, odist, FFTW_ESTIMATE);
    fftw_execute(plan);
    fftw_destroy_plan(plan);
}


void FFTAutocorr(double *& signal, double *& g2, int ntimes, int nrows) {

    /* calculate \int f(t) f(t+\tau) part */

    /* pad zeros to signal */
    size_t memsize = 2 * ntimes * nrows * sizeof(double);
    double * padded = (double *) fftw_malloc(memsize);

#pragma omp parallel for
    for (int i = 0; i < nrows; i++)
        for (int j = 0; j < 2*ntimes; j++) {
            int k = 2 * ntimes * i + j;
            if (j < ntimes) padded[k] = signal[ntimes * i + j];
            else padded[k]= 0.f;
        }

    /* Tell fftw about openmp */
    fftw_init_threads();
    fftw_plan_with_nthreads(omp_get_max_threads());

    /* allocate output memory */
    memsize = (ntimes + 1) * nrows * sizeof(fftw_complex);
    fftw_complex * spectra = (fftw_complex *) fftw_malloc(memsize);

    /* calculate fft */
    fft(padded, spectra, 2*ntimes, nrows);

    /* mulitply spectra by itself */
#pragma omp parallel for
    for (int i = 0; i < (ntimes+1)*nrows; i++) abs(spectra[i]);

    /* calculate inverse fft */
    ifft(spectra, padded, 2*ntimes, nrows);
    // rescale
#pragma omp parallel for
    for (int i = 0; i < 2*ntimes*nrows; i++)
        padded[i] /= 2*ntimes;
    
    /* calculate normalization <f(t)><f(t+\tau)> */
    double * sumall = (double *) fftw_malloc(nrows * sizeof(double));
    double * norm_l = (double *) fftw_malloc(ntimes * nrows * sizeof(double));
    double * norm_r = (double *) fftw_malloc(ntimes * nrows * sizeof(double));

    // calculate sum of all the time-series
#pragma omp parallel for
    for (int i = 0; i < nrows; i++) {
        sumall[i] = 0;
        for (int j = 0; j < ntimes; j++)
            sumall[i] += signal[i*ntimes+j];
    }

    // set boundaries
#pragma omp parallel for
    for (int i = 0; i < nrows; i++) {
        norm_l[i * ntimes] = sumall[i];
        norm_r[i * ntimes] = sumall[i];
    } 

    // calculate <I(t)>
#pragma omp parallel for
    for (int i = 0; i < nrows; i++) {
        int j_end = ntimes-1;
        for (int j = 1; j < ntimes; j++) {
            norm_l[i*ntimes+j] = norm_l[i*ntimes+j-1] - signal[i*ntimes + j_end];
            j_end--;
        }
    }

    // calculate <I(t+\tau)>
#pragma omp parallel for
    for (int i = 0; i < nrows; i++)
        for (int j = 1; j < ntimes; j++)
            norm_r[i*ntimes+j] = norm_r[i*ntimes+j-1] - signal[i*ntimes+j-1];

    // calculate g2
#pragma omp parallel for
    for (int i = 0; i < nrows; i++)
        for (int j = 0; j < ntimes; j++) {
            int k = i * ntimes + j;
            g2[k] = padded[i*2*ntimes+j] * (ntimes-j)
                    / ( norm_l[k] * norm_r[k] );
        }

    // free allocated blocks
    fftw_free(padded);
    fftw_free(spectra);
    fftw_free(sumall);
    fftw_free(norm_l);
    fftw_free(norm_r);
    fftw_cleanup();
}
