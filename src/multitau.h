
#ifndef MULTI_TAU_CORRELATOR__H
#define MULTI_TAU_CORRELATOR__H

class MultiTauAutocorrelator {
    private:
        const unsigned nrows_;
        const unsigned ncols_;
        unsigned ntime_;
        unsigned len_;
        unsigned idx_;
        float * signal_;
        float * g2s_;
        float * tau_; 
        
    public:
        MultiTauAutocorrelator(float *, unsigned, unsigned);
        ~MultiTauAutocorrelator();

        /* forbid copy and assignment operators */
        MultiTauAutocorrelator(const MultiTauAutocorrelator &) = delete;
        MultiTauAutocorrelator & operator==(const MultiTauAutocorrelator &) = delete;

        // expose g2 and lag-time arrays
        size_t length() const { return len_; }
        float * g2()  { return g2s_; }
        float * tau() { return tau_; }

        /* work horses */
        void reduceInplace();
        void run_level(unsigned);
        void process(unsigned m=16, float dt=1);
};

#endif // MULTI_TAU_CORRELATOR__H
