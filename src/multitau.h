
#ifndef MULTI_TAU_CORRELATOR__H
#define MULTI_TAU_CORRELATOR__H

class MultiTauAutocorrelator {
    private:
        const unsigned nrows_;
        const unsigned ncols_;
        unsigned ntime_;
        unsigned len_;
        unsigned idx_;
        double * signal_;
        double * g2s_;
        double * tau_; 
        
    public:
        MultiTauAutocorrelator(double *, unsigned, unsigned);
        ~MultiTauAutocorrelator();

        /* forbid copy and assignment operators */
        MultiTauAutocorrelator(const MultiTauAutocorrelator &) = delete;
        MultiTauAutocorrelator & operator==(const MultiTauAutocorrelator &) = delete;

        // expose g2 and lag-time arrays
        size_t length() const { return len_; }
        double * g2()  { return g2s_; }
        double * tau() { return tau_; }

        /* work horses */
        void reduceInplace();
        void run_level(unsigned);
        void process(unsigned m=16, double dt=1);
};

#endif // MULTI_TAU_CORRELATOR__H
