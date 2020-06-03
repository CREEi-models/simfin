import os
import pandas as pd
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))


class macro:
    def __init__(self,start_yr):
        self.rates = pd.read_pickle(module_dir+'/simfin/params/rates.pkl')
        self.infl = self.rates.loc['inflation','tcam_last5']
        self.g_pars = pd.read_pickle(module_dir+'/simfin/params/growth_params.pkl')
        self.data = pd.read_pickle(module_dir+'/simfin/params/base_aggregates.pkl')
        self.start_yr = start_yr
        self.Y = self.data['nom_Y']
        self.L = self.data['L']*1e3
        self.N = self.data['N']
        self.E_w = 0 # Sur quel agrégat.
        self.C_hh = self.data['C_hh']

        self.gr_K = self.g_pars['g_real_K']
        self.gr_A = self.g_pars['A']
        self.gr_L = 0.0
        self.gr_N = 0.0
        self.gr_Y = 0.0
        self.year = start_yr
        return
    def reset(self,pop,eco):
        self.infl = self.rates.loc['inflation','tcam_last5']
        self.Y = self.data['nom_Y']
        self.L = self.data['L']*1e3
        self.N = self.data['N']
        self.C_hh = self.data['C_hh']
        self.gr_K = self.g_pars['g_real_K']
        self.gr_A = self.g_pars['A']
        self.gr_L = 0.0
        self.gr_N = 0.0
        self.gr_Y = 0.0
        self.year = self.start_yr
        self.set_align_emp(pop,eco)

    def set_rate_real_K(self,rate=None):
        if rate!=None:
            self.gr_K = rate
        return
    def set_rate_TFP(self,rate=None):
        if rate!=None:
            self.gr_A = rate
        return
    def set_align_emp(self,pop,eco):
        wages = eco['earn_c']/eco['hours_c']
        self.eff_hours = wages/ wages.mean()
        L = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum()
        self.align = self.L/L
        return
    def set_align_cons(self,pop,eco):
        C = (pop.multiply(eco['cons'],fill_value=0.0).sum())
        align_c_hh = self.C_hh/C
        print('alignment factor for consommation : ',align_c_hh)
        eco['cons'] = eco['cons']*align_c_hh
        return


    def emp(self,pop,eco):
        L = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum() * self.align
        self.gr_L = np.log(L) - np.log(self.L)
        self.L = L
        return

    def work_earnings(self,pop,eco):
        E_w = pop.multiply(eco['emp']*eco['earn_c'],fill_value=0.0).sum()
        self.E_w = E_w
        return

    def cons(self,pop,eco):
        C_hh = (pop.multiply(eco['cons'],fill_value=0.0).sum())
        self.gr_C_hh = np.log(C_hh) - np.log(self.C_hh)
        self.C_hh = C_hh
        return
    def grow_cons(self,eco):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']*self.gr_A/2  # Part TFP non lié à l'éducation (50%)
        eco['cons'] *=   rate
    def grow_work_earnings(self,eco):
        """
        Fait croître les revenus de salaire par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']* self.gr_A/2  # Part TFP non lié à l'éducation (50%)
        eco['earn_c'] *=   rate

    def non_work_earnings(self,pop,eco): # B. Achou, pas sûr que cette fonction soit nécessaire
        E_wno = pop.multiply(eco['taxinc'],fill_value=0.0).sum()
        self.E_wno = E_wno
        return
    def grow_non_work_earnings(self,eco): # B. Achou
        """
        Fait croître les revenues autres que salaire par personne au rythme de l'inflation +
        1/alpha_L *la croissance de la TFP (A).
        """
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']* self.gr_A/2  # Part TFP non lié à l'éducation (50%)
        eco['taxinc'] *=   rate

    def pop(self,pop):
        N = pop.sum()
        self.gr_N = np.log(N) - np.log(self.N)
        self.N = N
        return
    def gdp(self):
        self.Y = self.Y * (1.0 + self.gr_Y + self.infl)
        return
    def grow(self,year):
        #self.gr_Y = self.gr_A + self.g_pars['alpha_K']*self.gr_K + self.g_pars['alpha_L']*self.gr_L
        self.gr_Y = 1/self.g_pars['alpha_L']*self.gr_A + self.gr_L
        self.gdp()
        self.year = year
        return
