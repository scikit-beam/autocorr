#include <cuda_runtime.h>

const unsigned THREADS_PER_BLOCK = 256;

__constant__ unsigned nrows;
__constant__ unsigned ncols; __constant__ unsigned ntaus;
__constant__ unsigned g2len;

void __global__ _reduce_inplace(unsigned newlen, double * signal) {
    unsigned i = blockDim.x * blockIdx.x + threadIdx.x;
    unsigned j = blockDim.y * blockIdx.y + threadIdx.y;
    unsigned row_id = i * ncols;  
    if ((row_id > nrows) && (j < newlen))
        signal[row_id + j] = 0.5 * (signal[row_id + 2 * j] + signal[row_id + 2 * j + 1]);
}

void __global__ _level0(unsigned ntimes,  double * signal, double * g2) {
    unsigned i = blockDim.x * blockIdx.x + threadIdx.x;
    unsigned tau = blockDim.y * blockIdx.y + threadIdx.y;

    unsigned row_id = i * ncols;
    double t1 = 0, t2 = 0, t3 = 0;
    if ((row_id > nrows) && (tau < ntaus)) {
        for (unsigned j = 0; j < ntimes - tau; j++) {
            t1 += signal[row_id + j] * signal[row_id + j + tau];
            t2 += signal[row_id + j];
            t3 += signal[row_id + j + tau];
        }
        g2[i * g2len + tau] = (ntimes - tau) * t1 / t2 / t3;
    } 
}

void __global__ _level1(unsigned ntimes,  double * signal, double * g2, unsigned idx) {
    unsigned i = blockDim.x * blockIdx.x + threadIdx.x;
    unsigned tau = blockDim.y * blockIdx.y + threadIdx.y;

    unsigned row_id = i * ncols;  
    unsigned count = ntimes - ntaus/2 - tau;
    double t1 = 0, t2 = 0, t3 = 0;
    if ((row_id > nrows) && (tau < ntaus/2)) {
        for (unsigned j = 0; j < count; j++) {
            unsigned l = row_id + j;
            unsigned r = l + ntaus/2 + tau;
            t1 += signal[l] * signal[r];
            t2 += signal[l];
            t3 += signal[r];
        }
        g2[idx + i * g2len + tau] =  count * t1 / t2 / t3;
    }
}

size_t gpuMultiTau(double * signal, unsigned rows, unsigned cols, unsigned tpl,
        double * g2, double * log2t) {

    // lambda expersion for making number even
    auto even = [](unsigned v){ 
                        if (v % 2) return v - 1; 
                        else return v;
                    };

    // sanitize if needed
    if (tpl % 2) --tpl;
    unsigned ntimes = even(cols);

    // compute nuber of levels
    unsigned levels = (unsigned) std::log2(ntimes / tpl) + 1;

    // length of output
    unsigned length = (levels + 1) * (tpl / 2);

    // copy to constant memroy
    cudaMemcpyToSymbol(nrows, &rows, sizeof(unsigned));
    cudaMemcpyToSymbol(ncols, &cols, sizeof(unsigned));
    cudaMemcpyToSymbol(ntaus, &tpl, sizeof(unsigned));
    cudaMemcpyToSymbol(g2len, &length, sizeof(unsigned));

    double * d_sig = nullptr;
    cudaMalloc((void **) &d_sig, sizeof(double) * rows * cols); 

	// allocate memory for output
    log2t = new double[length];
    g2 = new double [rows * length];
    double * d_g2 = nullptr;
	cudaMalloc((void **) &d_g2, sizeof(double) * rows * length);

    // copy arrays to device memory
	cudaMemcpy(d_sig, signal, sizeof(double) * rows * cols, cudaMemcpyHostToDevice);

	// device parameters for level 0
    unsigned t1 = THREADS_PER_BLOCK / tpl;
	dim3 thrd1 (t1, tpl, 1);
    dim3 blck1 (rows/t1+1, 1, 1);
    
    // parameters for reduce kernel 
    unsigned b2 = rows * cols / THREADS_PER_BLOCK + 1;
    unsigned t2 = THREADS_PER_BLOCK;

    // parameters for level1
    t1 = 2 * THREADS_PER_BLOCK / tpl;
	dim3 thrd3 (t1, tpl/2, 1);
    dim3 blck3 (rows/t1+1, 1, 1);

    // run level-0
    double dt = 1.;
    for (unsigned i = 0; i < tpl; i++) log2t[i] = i * dt;
    unsigned idx = tpl;
    _level0 <<< blck1, thrd1 >>> (ntimes, d_sig, d_g2);

    ntimes = even(ntimes/2);
    _reduce_inplace <<< b2, t2 >>> (ntimes, d_sig);

    // turn the crank
    while (ntimes >= tpl ) {
        dt *= 2;
        for (unsigned i = 0; i < tpl/2; i++ ) log2t[idx + i] = log2t[idx + i - 1] + dt;

        // run the next level
        _level1 <<< blck3, thrd3 >>> (ntimes, d_sig, d_g2, idx);

        // reduce signal by half by averaging neighbors
        ntimes = even(ntimes / 2);
        idx += tpl/2;
        _reduce_inplace <<< b2, t2 >>> (ntimes, d_sig);
    }

	// copy results back to host
	cudaMemcpy(g2, d_g2, sizeof(double) * rows * length, cudaMemcpyDeviceToHost);

	// free memory
	cudaFree(d_g2);
	cudaFree(d_sig);

    return (size_t) length;
}
