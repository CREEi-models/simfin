import os
import pandas as pd
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))
from itertools import product
import pickle

class macro:
    def __init__(self,start_yr):
        #self.rates = pd.read_csv(module_dir+'/simfin/params/rates.csv')
        self.g_pars = pd.read_csv(module_dir+'/simfin/params/growth_params.csv', index_col=0, header=None,sep = ';')
        self.data = pd.read_csv(module_dir+'/simfin/params/base_aggregates.csv', index_col=0, header=None,sep = ';')
        self.start_yr = start_yr
        gdp = pd.read_excel(module_dir+'/simfin/params/historical_accounts.xlsx',sheet_name='Inputs')
        self.gr = pd.read_excel(module_dir+'/simfin/params/gr_A.xlsx',sheet_name='gr_A')
        self.gr = self.gr.set_index('var')
        self.Yp = gdp.at[34,2021]
        self.Y = self.Yp
        self.L = self.data.loc['L',1]*1e3
        self.Lp = self.L
        self.N = self.data.loc['N',1]
        self.E_w = 0 # Sur quel agrégat.
        self.C_hh = self.data.loc['C_hh',1]
        self.gr_K = self.g_pars.loc['g_real_K',1]
        self.gr_A = 0.0
        self.infl = 0.02
        self.gr_L = 0.0
        self.gr_Lp = 0.0
        self.gr_N = 0.0
        self.gr_Y = 0.0
        self.gr_Yp = 0.0
        self.year = start_yr
        return
    def reset(self,pop,eco):
        self.infl = 0.02
        self.Y = self.data.loc['nom_Y',1]
        self.L = self.data.loc['L',1]*1e3
        self.N = self.data.loc['N',1]
        self.C_hh = self.data.loc['C_hh',1]
        self.gr_K = self.g_pars.loc['g_real_K',1]
        self.gr_A = 0.0
        self.gr_L = 0.0
        self.gr_N = 0.0
        self.gr_Y = 0.0
        self.year = self.start_yr
        self.set_align_emp(pop,eco)
    def grow_tfp(self,year):
        self.gr_A=self.gr_A
        return
    def grow_infl(self,year):
        self.infl=self.infl
        return
    def set_align_emp(self,pop,eco):
        wages = eco['earn_c']/eco['hours_c']
        self.eff_hours = wages/ wages.mean()
        L = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum()
        self.align = self.L/L
        self.employment = pop.multiply(eco['emp'],fill_value=0.0).sum()
        self.employment_25_54 = pop.multiply(eco.query('age >= 25 and age <= 54')['emp'],fill_value=0.0).sum()
        self.employment_60_69 = pop.multiply(eco.query('age >= 60 and age <= 69')['emp'],fill_value=0.0).sum()
        self.hours = pop.multiply(eco['hours_c'],fill_value=0.0).mean() * self.align
        return
    def set_align_cons(self,pop,eco):
        C = (pop.multiply(eco['cons'],fill_value=0.0).sum())
        align_c_hh = self.C_hh/C
        eco['cons'] = eco['cons']*align_c_hh
        return
    def emp(self,pop,eco,year):
        L = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum() * self.align
        self.gr_L = L/ self.L-1
        self.L = L
        self.employment = pop.multiply(eco['emp'],fill_value=0.0).sum()
        self.employment_25_54 = pop.multiply(eco.query('age >= 25 and age <= 54')['emp'],fill_value=0.0).sum()
        self.employment_60_69 = pop.multiply(eco.query('age >= 60 and age <= 69')['emp'],fill_value=0.0).sum()
        self.hours = pop.multiply(eco['hours_c'],fill_value=0.0).mean() * self.align
        Lp = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum() * self.align
        self.gr_Lp = Lp/ self.Lp-1
        self.Lp = Lp
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
    def grow_cons(self,eco,year):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars.loc['alpha_L',1]*self.gr.loc['gr_A',self.year] # Part TFP non lié à l'éducation (50%)
        eco['cons'] = eco['cons']*rate
        sum = eco['cons'].sum()
    def grow_work_earnings(self,eco,year):
        """
        Fait croître les revenus de salaire par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        index = eco.index
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars.loc['alpha_L',1]*self.gr.loc['gr_A',self.year] # Part TFP non lié à l'éducation (50%)
        eco['earn_c'] = eco['earn_c']*rate
    def non_work_earnings(self,pop,eco): # B. Achou, pas sûr que cette fonction soit nécessaire
        E_wno = pop.multiply(eco['taxinc'],fill_value=0.0).sum()
        self.E_wno = E_wno
        return
    def grow_non_work_earnings(self,eco,year): # B. Achou
        """
        Fait croître les revenues autres que salaire par personne au rythme de l'inflation +
        1/alpha_L *la croissance de la TFP (A).
        """
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars.loc['alpha_L',1]*self.gr.loc['gr_A',self.year]  # Part TFP non lié à l'éducation (50%)
        eco['taxinc'] = eco['taxinc']*rate
    def pop(self,pop):
        N = pop.sum()
        self.gr_N = np.log(N) - np.log(self.N)
        self.N = N
        return
    def gdp(self):
        self.Y = self.Y * (1.0 + self.gr_Y + self.infl)
        self.Yp = self.Yp * (1.0 + self.gr_Yp + self.infl)
        return
    def grow(self,year):
        self.gr_Y = 1/self.g_pars.loc['alpha_L',1]*self.gr.loc['gr_A',self.year] + self.gr_L
        self.gr_Yp = 1/self.g_pars.loc['alpha_L',1]*self.gr.loc['gr_A',self.year] + self.gr_Lp
        self.gdp()
        self.year = year
        return
