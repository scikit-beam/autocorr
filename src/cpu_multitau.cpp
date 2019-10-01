#include <algorithm>
#include <cmath>
#include <cstring>

#include <iostream>
#include "autocorr.h"

MultiTauAutocorrelator:: MultiTauAutocorrelator(double * data, unsigned row, unsigned col):
    nrows_(row), ncols_(col), ntime_(col), idx_(0), len_(0) {
    if (ntime_ % 2) ntime_--;

    signal_ = new double[nrows_ * ncols_];
    std::memcpy(signal_, data, sizeof(double) * nrows_ * ncols_);
    g2s_ = nullptr;
    tau_ = nullptr;
}
        
MultiTauAutocorrelator::~MultiTauAutocorrelator(){
    if (signal_) delete [] signal_;
    if (g2s_)    delete [] g2s_;
    if (tau_)    delete [] tau_;
}
        
void MultiTauAutocorrelator::reduceInplace(){
#pragma omp parallel for 
    for (unsigned j = 0; j < nrows_; j++){
        unsigned row_id = j * ncols_;
        for (unsigned i = 0; i < ntime_; i++)
            signal_[row_id + i] = 0.5 * (signal_[row_id + 2*i] + signal_[row_id + 2*i + 1]);
    }
}

void MultiTauAutocorrelator::run_level(unsigned ntaus) {
    int m = idx_ ? 1 : 0;

#pragma omp parallel for collapse(2)
    for (unsigned j = 0; j < nrows_; j++) {
        for (unsigned tau = 0; tau < ntaus; tau++) {
            double t1 = 0, t2 = 0, t3 =0;
            unsigned shift = m * ntaus;
            unsigned row_id = j * ncols_;
            unsigned count = ntime_ - shift - tau;
            for (unsigned i = 0; i < count; i++) {

                unsigned l = row_id + i;
                unsigned r = l + shift + tau;
                t1 += signal_[l] * signal_[r];
                t2 += signal_[l];
                t3 += signal_[r];
            }
            g2s_[idx_ + j * len_ +  tau] = (t1 * count) / (t2 * t3 );
        }
    }
}

void MultiTauAutocorrelator::process(unsigned tpl, double dt) {
    if (tpl % 2) tpl--;
    unsigned levels = (unsigned) std::log2(ntime_/tpl) + 1; 
    len_ = (levels + 1 ) * (tpl / 2);
    tau_ = new double[len_];
    g2s_ = new double[nrows_ * len_];
    
    /* run the process once with full tau width */
    for (unsigned i = 0; i < tpl; i++) tau_[i] = i * dt;
    run_level(tpl);
    idx_ += tpl;

    // half the length of signal
    ntime_ /= 2;
    if (ntime_ % 2) ntime_--;
    // reduce data by averaging adjecent neighbours
    reduceInplace();

    /* 
     * process rest of the levels successively with :
     * twice the time-step, and
     * reduced signal successively.  
     * */ 
    while ( ntime_ >= tpl ) {

        dt *= 2;
        for (unsigned i = 0; i < tpl/2; i++)
            tau_[idx_ + i] = tau_[idx_ + i -1] + dt;

        // each level not ZERO is run for half the lag-times
        run_level(tpl/2);

        // reduce the data
        idx_ += tpl/2;
        ntime_ /= 2;
        if (ntime_ % 2) ntime_--;
        reduceInplace();
    }
}
