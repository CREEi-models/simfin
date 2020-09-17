import os
import pandas as pd
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))
from itertools import product
import pickle

class macro:
    def __init__(self,start_yr):
        self.rates = pd.read_pickle(module_dir+'/simfin/params/rates.pkl')
        self.infl = 2/100#self.rates.loc['inflation','tcam_last5']
        self.g_pars = pd.read_pickle(module_dir+'/simfin/params/growth_params.pkl')
        self.data = pd.read_pickle(module_dir+'/simfin/params/base_aggregates.pkl')
        self.start_yr = start_yr
        #self.Y = self.data['nom_Y']
        #self.Y = 453572
        gdp = pd.read_excel(module_dir+'/simfin/params/historical_accounts.xlsx',sheet_name='Inputs')
        self.Y = gdp.at[34,2020]
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
    def set_shocks(self,shocks):
        self.shocks = shocks
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
        wages = eco['earn_c']/eco['hours_c']
        self.eff_hours = wages/ wages.mean()
        L = pop.multiply(eco['emp']*eco['hours_c']*self.eff_hours,fill_value=0.0).sum()
        self.align = self.L/L
        return
    def set_align_cons(self,pop,eco):
        C = (pop.multiply(eco['cons'],fill_value=0.0).sum())
        align_c_hh = self.C_hh/C
        #print('alignment factor for consommation : ',align_c_hh)
        eco['cons'] = eco['cons']*align_c_hh
        return
    def emp(self,pop,eco,year):
        shocks = self.shocks['emp'].loc[:,year]*self.shocks['hours_c'].loc[:,year]
        L = pop.multiply(eco['emp']*eco['hours_c']*shocks*self.eff_hours,fill_value=0.0).sum() * self.align
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
    def grow_cons(self,eco,year):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        shocks = self.shocks['cons'].loc[:,year]/self.shocks['cons'].loc[:,year-1]
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']*self.gr_A  # Part TFP non lié à l'éducation (50%)
        eco['cons'] = eco['cons']*shocks*rate
    def grow_work_earnings(self,eco,year):
        """
        Fait croître les revenus de salaire par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A).
        """
        index = eco.index
        shocks = (self.shocks['emp'].loc[:,year]*self.shocks['earn_c'].loc[:,year]) / (self.shocks['emp'].loc[:,year-1]*self.shocks['earn_c'].loc[:,year-1])
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']* self.gr_A  # Part TFP non lié à l'éducation (50%)
        eco['earn_c'] = eco['earn_c']*shocks*rate
    def non_work_earnings(self,pop,eco): # B. Achou, pas sûr que cette fonction soit nécessaire
        E_wno = pop.multiply(eco['taxinc'],fill_value=0.0).sum()
        self.E_wno = E_wno
        return
    def grow_non_work_earnings(self,eco,year): # B. Achou
        """
        Fait croître les revenues autres que salaire par personne au rythme de l'inflation +
        1/alpha_L *la croissance de la TFP (A).
        """
        shocks = self.shocks['taxinc'].loc[:,year]/self.shocks['taxinc'].loc[:,year-1]
        igra = True
        rate = 1.0+self.infl
        if igra == True:
            rate += 1/self.g_pars['alpha_L']* self.gr_A  # Part TFP non lié à l'éducation (50%)
        eco['taxinc'] = eco['taxinc']*shocks*rate
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
        #print("Le taux de croissance est", self.gr_Y)
        self.gdp()
        self.year = year
        return


class covid:
    def __init__(self,start_index,start_yr,start_lockdown,stop_yr,recovery_rate_short=0.25,recovery_rate_long=0.25,recovery_rate_cons=0.25,
            second_wave=False,second_lockdown_time='2021Q4',lockdown_force=1.0):
        self.index = start_index
        self.start_yr = start_yr
        self.start_lockdown = start_lockdown
        self.stop_yr = stop_yr
        self.second_wave = second_wave
        self.second_lockdown_time = second_lockdown_time
        self.lockdown_force = lockdown_force
        self.recovery_rate_short = recovery_rate_short
        self.recovery_rate_long = recovery_rate_long
        self.recovery_rate_cons= recovery_rate_cons
        frame = pd.DataFrame(index=start_index)
        self.years = np.arange(start_yr,stop_yr)
        months = [1,4,7,10]
        temp = list(product(*[self.years,months]))
        yr = [t[0] for t in temp]
        qs = [t[1] for t in temp]
        dates = pd.DataFrame({'year':yr,'month':qs})
        dates['day'] = 1
        self.datef = pd.to_datetime(dates).dt.to_period('Q')
        for d in self.datef:
            frame[d] = 1.0
        self.outcomes = ['emp','hours_c','earn_c','taxinc','cons']
        self.load_params()
        shocks = []
        for o in self.outcomes:
            shocks.append(frame.copy())
        self.shocks = dict(zip(self.outcomes,shocks))
        for o in self.outcomes:
            self.predict(o)
        # initialize additional spending & income
        accounts = ['health','educ','family','economy','justice','transfers','gov_enterprises','personal_taxes','corporate_taxes','property_taxes']
        self.plan = pd.DataFrame(index=accounts,columns=np.arange(start_yr,stop_yr))
        for v in self.plan.columns:
            self.plan[v] = self.plan[v].astype('float')
        self.plan.loc[:,:] = 0.0
        self.set_plan()
        return
    def load_params(self):
        self.par_shocks = pd.read_csv(module_dir+'/simfin/params/COVID_age_effects.csv',sep=',')
        self.par_shocks = self.par_shocks.set_index('var')
        return
    def predict(self,outcome):
        work = pd.DataFrame(index=self.index)
        work['age'] = work.index.get_level_values(0).to_list()
        work['male'] = work.index.get_level_values(1).to_list()
        work['educ'] = work.index.get_level_values(3).to_list()
        work['married'] = work.index.get_level_values(4).to_list()
        work['age2529'] = (work['age']>=25) & (work['age']<=29)
        work['age3034'] = (work['age']>=30) & (work['age']<=34)
        work['age3539'] = (work['age']>=35) & (work['age']<=39)
        work['age4549'] = (work['age']>=45) & (work['age']<=49)
        work['age5054'] = (work['age']>=50) & (work['age']<=54)
        work['age5559'] = (work['age']>=55) & (work['age']<=59)
        work['age6064'] = (work['age']>=60) & (work['age']<=64)
        work['des'] = work['educ']=='des'
        work['dec'] = work['educ']=='dec'
        work['uni'] = work['educ']=='uni'
        beta = self.par_shocks.loc[:,outcome]
        work['mu'] = beta['constant']
        for c in beta.index.to_list()[:1]:
            work['mu'] += beta[c]*work[c]
        if outcome=='emp':
            work['pr'] = np.exp(work['mu'])/(1+np.exp(work['mu']))
            work.loc[work['age']<=24,'pr'] = work.loc[work['age']==25,'pr'].mean()
            work.loc[work['age']>=65,'pr'] = work.loc[work['age']==64,'pr'].mean()
        else :
            work['pr'] = 1.0 + work['mu']
            work.loc[work['age']<=24,'pr'] = work.loc[work['age']==25,'pr'].mean()
            work.loc[work['age']>=65,'pr'] = work.loc[work['age']==64,'pr'].mean()
        # find monthly recovery rate (for a trimester divide by 2 given effect of first month)
        recovery_rate_monthly = self.recovery_rate_short/2
        factor = 1 - (1-work['pr'])*(1.0 + np.exp(-recovery_rate_monthly) + np.exp(-recovery_rate_monthly*2))/3.0
        factor_cons = 1 - (1-work['pr'])
        if outcome=='cons':
            self.shocks[outcome].loc[:,self.start_lockdown] = factor_cons
        else :
            self.shocks[outcome].loc[:,self.start_lockdown] = factor
        return
    def construct(self):
        lastq = self.start_lockdown
        time_since_lockdown = 0
        for q in self.datef:
            if q>pd.Period(self.start_lockdown):
                time_since_lockdown +=1
                time_since_lockdown_cons=0
                if time_since_lockdown>=5:
                    time_since_lockdown_cons +=1
                for o in self.outcomes:
                    if o=='cons' and time_since_lockdown==0:
                        self.shocks[o].loc[:,q] = 1-(1-self.shocks[o].loc[:,lastq])
                    #print(self.shocks['cons'].loc[:,'2020Q1'].mean())
                    #if o=='cons' and (time_since_lockdown==1 or time_since_lockdown==2 or time_since_lockdown==3):
                    #    self.shocks[o].loc[:,q] = 1-(0.014)
                        #print(self.shocks[o].loc[:,q])
                    if o=='cons' and time_since_lockdown>0:
                        self.shocks[o].loc[:,q] = 1

                    #if o=='cons' and time_since_lockdown==0:
                    #    self.shocks[o].loc[:,q] = 1-(1-self.shocks[o].loc[:,lastq])
                    #if o=='cons' and (time_since_lockdown==1 or time_since_lockdown==2 or time_since_lockdown==3):
                    #    self.shocks[o].loc[:,q] = 1-(0.02)
                    #if o=='cons' and time_since_lockdown>3:
                    #    self.shocks[o].loc[:,q] = 1

                    #if o=='cons' and time_since_lockdown==0:
                    #    self.shocks[o].loc[:,q] = 1-(1-self.shocks[o].loc[:,lastq])
                    #if o=='cons' and time_since_lockdown>0:
                    #    self.shocks[o].loc[:,q] = 1

                    if o!='cons':
                        self.shocks[o].loc[:,q] = 1-(1-self.shocks[o].loc[:,lastq])*np.exp(-self.recovery_rate_long*time_since_lockdown)
                #print(self.shocks['cons'].loc[0,'2022Q1'])
                #print(self.shocks['cons'].loc[:,lastq])

                #On enlève le chock après le premier trimestre de 2020-2021 sur la consommation (Q3 2020) : plus d'effet au second trimestre (https://thoughtleadership.rbc.com/covid-consumer-spending-tracker/)
                #if time_since_lockdown>=1 and o=='cons':
                #        self.shocks[o].loc[:,q] = 1
                #if self.second_wave:
                #    if pd.Period(q)==pd.Period(self.second_lockdown_time):
                #        time_since_lockdown = 0
                #        for o in self.outcomes:
                            #print(time_since_lockdown)
                            #lockdown_shock = self.shocks[o].loc[:,self.start_lockdown]
                            #self.shocks[o].loc[:,q] = 1-self.lockdown_force*(1-lockdown_shock)*np.exp(-self.recovery_rate_long*time_since_lockdown)
                            #if o=='cons' and time_since_lockdown>0 and time_since_lockdown<4:
                            #    print('yeah!')
                            #    self.shocks[o].loc[:,q] = 1-self.lockdown_force*(1-lockdown_shock)
                            #else:
                            #    self.shocks[o].loc[:,q] = 1-self.lockdown_force*(1-lockdown_shock)*np.exp(-self.recovery_rate_long*time_since_lockdown)
                if self.second_wave:
                    if pd.Period(q)==pd.Period(self.second_lockdown_time):
                        time_since_lockdown = 0
                        for o in self.outcomes:
                            lockdown_shock = self.shocks[o].loc[:,self.start_lockdown]
                            self.shocks[o].loc[:,q] = 1-self.lockdown_force*(1-lockdown_shock)*np.exp(-self.recovery_rate_long*time_since_lockdown)
                lastq = q
        return
    def aggregate(self,to_year=2060):
        shock_aggregates = []
        for o in self.outcomes:
            frame = pd.DataFrame(index=self.index)
            for t in self.years:
                frame[t] = self.shocks[o].loc[:,[c for c in self.shocks[o].columns if c.year==t]].mean(axis=1)
            for t in range(self.stop_yr,to_year):
                frame[t] = 1.0
            shock_aggregates.append(frame)
        self.shock_aggregates = dict(zip(self.outcomes,shock_aggregates))
        #print(self.shock_aggregates)
        return
    def set_plan(self,to_year=2060):
        inject = pd.read_csv(module_dir+'/simfin/params/COVID_plan.csv',sep=',')
        inject = inject.set_index('accounts')
        plan = inject['amount'].to_dict()
        if self.second_wave:
            scale = 1 + self.lockdown_force
        else :
            scale = 1
        self.plan.loc['health',2021] = plan['health']*scale
        self.plan.loc['educ',2021] = plan['educ']*scale
        self.plan.loc['family',2021] = plan['family']*scale
        self.plan.loc['economy',2021] = plan['economy']*scale
        self.plan.loc['justice',2021] = plan['justice']*scale
        self.plan.loc['transfers',2021] = plan['transfers']*scale
        self.plan.loc['gov_enterprises',2021] = plan['gov_enterprises']*scale
        self.plan.loc['personal_taxes',2021] = plan['personal_taxes']*scale
        self.plan.loc['corporate_taxes',2021] = plan['corporate_taxes']*scale
        self.plan.loc['property_taxes',2021] = plan['property_taxes']*scale
        for t in range(self.stop_yr,to_year):
            self.plan[t] = 0.0
        return
