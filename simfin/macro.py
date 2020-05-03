import os
import pandas as pd
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))


class macro: 
    def __init__(self,start_yr):
        rates = pd.read_pickle(module_dir+'/simfin/params/rates.pkl')
        self.infl = rates.loc['inflation','tcam_last5']
        self.g_pars = pd.read_pickle(module_dir+'/simfin/params/growth_params.pkl')
        self.data = pd.read_pickle(module_dir+'/simfin/params/base_aggregates.pkl')
        self.start_yr = start_yr
        self.Y = self.data['nom_Y']
        self.L = self.data['L']*1e3
        self.N = self.data['N']
        self.gr_K = self.g_pars['g_real_K']
        self.gr_A = self.g_pars['A']
        self.gr_L = 0.0
        self.gr_N = 0.0
        self.gr_Y = 0.0
        self.year = start_yr
        return 
    def set_rate_real_K(self,rate=None):
        if rate!=None:
            self.gr_K = rate 
        return 
    def set_rate_TFP(self,rate=None):
        if rate!=None:
            self.gr_A = rate 
        return 
    def set_align_emp(self,pop,eco):
        L = pop.multiply(eco['emp']*eco['hours'],fill_value=0.0).sum()
        self.align = self.L/L
        return 
    def emp(self,pop,eco):
        L = pop.multiply(eco['emp']*eco['hours'],fill_value=0.0).sum() * self.align
        self.gr_L = np.log(L) - np.log(self.L)
        self.L = L
        return 
    def pop(self,pop):
        N = pop.sum()
        self.gr_N = np.log(N) - np.log(self.N)
        self.N = N
        return 
    def gdp(self):
        self.Y = self.Y * (1.0 + self.gr_Y + self.infl)
        return 
    def grow(self,year):
        self.gr_Y = self.gr_A + self.g_pars['alpha_K']*self.gr_K + self.g_pars['alpha_L']*self.gr_L
        self.gdp()
        self.year = year
        return 
