import os
import pandas as pd
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))

from itertools import product
import pickle
from statsmodels.tsa.filters.hp_filter import hpfilter as hp
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.base.datetools import dates_from_str
from statsmodels.tsa.api import VAR
from simfin import shocks

class macro:
    def __init__(self,start_yr, stop_yr,stochastic=True):
        self.start_yr = start_yr
        self.stop_yr = stop_yr
        self.stochastic = stochastic
        self.load_aggregates()
        self.set_shocks()
        self.set_gr_YperH_rates()
        self.set_infl_rate()
        self.set_sp500()
        self.set_b1yr_rates()
        self.set_b5yr_spread()
        self.set_b10yr_spread()
        self.set_b30yr_spread()
        self.set_infl_rate()
        return
    def load_aggregates(self):
        self.hist_aggr_q = pd.read_excel(
            module_dir+'/simfin/params/macro_q.xlsx',sheet_name='data')
        self.hist_aggr_q.set_index(['year','q'],inplace=True)

        self.hist_aggr_yr = pd.read_excel(
            module_dir+'/simfin/params/macro.xlsx',sheet_name='data')
        self.hist_aggr_yr.set_index('year',inplace=True)
        # starting with aggregates from 2020
        self.Y = self.hist_aggr_yr.loc[self.start_yr-1,'Y']
        self.Yp = self.Y
        self.N = self.hist_aggr_yr.loc[self.start_yr-1,'N']
        # workers in thousands (put back in numbers)
        self.E = self.hist_aggr_yr.loc[self.start_yr-1,'E']*1e3
        # use 2020 hours worked, sum over all 4 quarters
        self.H = self.hist_aggr_q.groupby('year').sum().loc[self.start_yr-1,'H']
        self.aggr = pd.DataFrame(index=np.arange(self.start_yr,self.stop_yr),
                                 columns=['Y','Yp','H','E','N','infl',
                                          'YperH','sp500','b1yr','b5yr',
                                          'b10yr','b30yr','gr_wage','gr_Y',
                                          'gr_H','gr_Yp','gr_YperH'])
        return
    def set_align(self,pop,eco):
        E = pop.multiply(eco['emp'],fill_value=0.0).sum()
        align = self.E/E
        eco['emp'] *= align
        H = pop.multiply(eco['emp']*eco['hours_c'],fill_value=0.0).sum()
        align = self.H/H
        eco['hours_c'] *= align
        return eco
    def set_shocks(self):
        df = self.hist_aggr_q.loc[:,:]
        df = df.reset_index()
        for q in range(1, 5):
            df['quarter_' + str(q)] = np.where(df['q'] == q, 1, 0)
        df['spread5yr'] = df['b5yr'] - df['b1yr']
        df['spread10yr'] = df['b10yr'] - df['b5yr']
        df['spread30yr'] = df['b30yr'] - df['b10yr']
        df['gr_YperH'] = df['YperH']/df['YperH'].shift(1)-1
        df['gr_H'] = df['H']/df['H'].shift(1)-1
        outcomes = ['gr_YperH','gr_H','infl','sp500','b1yr','spread5yr','spread10yr',
                  'spread30yr']
        for o in outcomes:
            c, t = hp(df[o].dropna())
            df.loc[~df[o].isna(),o + '_t'] = t
            df.loc[~df[o].isna(),o + '_c'] = c
        outcomes_c = [c+'_c' for c in  outcomes]
        outcomes_t = [c + '_t' for c in outcomes]
        dates = df[['year', 'q']].astype(int).astype(str)
        quarterly = dates["year"] + "Q" + dates["q"]
        quarterly = dates_from_str(quarterly)
        df.index = pd.DatetimeIndex(quarterly)
        self.df_for_shocks = df
        data = df.dropna()
        data_est = data.loc[(data.index.year<=2019),:]
        model = VAR(data_est[outcomes_c],exog=data_est[['quarter_2',
                                                        'quarter_3',
                                            'quarter_4']])
        results = model.fit(1)
        lags = results.coefs
        params = pd.DataFrame(index=outcomes, columns=outcomes,
                              data=lags[0, :, :])
        const = results.coefs_exog
        exog_params = pd.DataFrame(index=outcomes_c,
                                   columns=['const', 'q2', 'q3', 'q4'],
                                   data=const)
        for q in [2,3,4]:
            exog_params['const_q'+str(q)] = exog_params['const'] + \
                                           exog_params['q'+str(q)]
        exog_params['const_q1'] = exog_params['const']
        const = ['const_q' + str(q) for q in range(1, 5)]
        icepts = exog_params[const]
        icepts.index = outcomes
        icepts.columns = [1,2,3,4]
        covar = results.resid.cov()
        covar = pd.DataFrame(index=outcomes_c, columns=outcomes_c, data=covar)
        covar.index = outcomes
        covar.columns = outcomes
        self.shocks = shocks(icepts,params,covar,self.stochastic)
        # initializing
        period = (data.index.year==2020) & (data.index.quarter==4)
        last_shocks = data.loc[period,outcomes_c].iloc[0,:]
        last_shocks.index = outcomes
        self.shocks.start_from(last_shocks)
        last_trend = data.loc[period,outcomes_t].iloc[0,:]
        last_trend.index = outcomes
        self.last_trend = last_trend
        return
    def set_gr_YperH_rates(self,current_rate=0.035,lt_rate=0.0125, catch_yr =
        2025):
        self.base_gr_YperH = pd.Series(index=np.arange(self.start_yr,
                                                     self.stop_yr))
        self.base_gr_YperH[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_gr_YperH[yr] = current_rate + slope*(yr -
                                                              self.start_yr)
                else :
                    self.base_gr_YperH[yr] = lt_rate
        return
    def set_b1yr_rates(self,current_rate = 0.005,lt_rate=0.01, catch_yr = 2035):
        self.base_b1yr = pd.Series(index=np.arange(self.start_yr,self.stop_yr))
        self.base_b1yr[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_b1yr[yr] = current_rate + slope*(yr - self.start_yr)
                else :
                    self.base_b1yr[yr] = lt_rate
        return
    def set_b5yr_spread(self,current_rate = 0.01, lt_rate = 0.01,catch_yr=2035):
        self.base_b5yr_spread = pd.Series(index=np.arange(self.start_yr,
                                                     self.stop_yr))
        self.base_b5yr_spread[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_b5yr_spread[yr] = current_rate + slope*(yr -
                                                               self.start_yr)
                else :
                    self.base_b5yr_spread[yr] = lt_rate
        return
    def set_b10yr_spread(self,current_rate = 0.01, lt_rate = 0.01,
                         catch_yr=2035):
        self.base_b10yr_spread = pd.Series(index=np.arange(self.start_yr,
                                                     self.stop_yr))
        self.base_b10yr_spread[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_b10yr_spread[yr] = current_rate + slope*(yr -
                                                               self.start_yr)
                else :
                    self.base_b10yr_spread[yr] = lt_rate
        return
    def set_b30yr_spread(self,current_rate = 0.01, lt_rate = 0.01,
                         catch_yr=2035):
        self.base_b30yr_spread = pd.Series(index=np.arange(self.start_yr,
                                                     self.stop_yr))
        self.base_b30yr_spread[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_b30yr_spread[yr] = current_rate + slope*(yr -
                                                               self.start_yr)
                else :
                    self.base_b30yr_spread[yr] = lt_rate
        return
    def set_sp500(self,current_rate = 0.08, lt_rate=0.07,catch_yr = 2025):
        self.base_sp500 = pd.Series(index=np.arange(self.start_yr,self.stop_yr))
        self.base_sp500[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_sp500[yr] = current_rate + slope*(yr - self.start_yr)
                else :
                    self.base_sp500[yr] = lt_rate
        return
    def set_infl_rate(self,current_rate=0.04,lt_rate=0.02,catch_yr = 2027):
        self.base_inflrate = pd.Series(index=np.arange(self.start_yr,self.stop_yr))
        self.base_inflrate[self.start_yr] = current_rate
        slope = (lt_rate - current_rate)/(catch_yr - self.start_yr)
        for yr in range(self.start_yr+1,self.stop_yr):
                if yr<=catch_yr:
                    self.base_inflrate[yr] = current_rate + slope*(yr - self.start_yr)
                else :
                    self.base_inflrate[yr] = lt_rate
        return
    def update_rates(self,yr,eco,pop):
        # base rates for that year
        shocks = self.shocks.update_1yr()
        # productivity growth rate
        self.gr_YperH_p = self.base_gr_YperH[yr]
        gr_YperH_t = (1+self.base_gr_YperH[yr])**(1/4)-1
        if self.stochastic:
            gr_YperH_c = shocks.loc['gr_YperH',:].to_numpy()
        else :
            gr_YperH_c = np.zeros(4)
        gr_YperH = np.product([(1.0+gr_YperH_t + gr_YperH_c[q]) for q in range(4)])
        self.gr_YperH = gr_YperH-1
        # hours growth rate
        H = pop.multiply(eco['emp']*eco['hours_c'],
                                  fill_value=0.0).sum()
        gr_H_t = H / self.H - 1
        self.gr_H_p = gr_H_t
        # compute growth rate if hours
        gr_H_t = (1+gr_H_t)**(1/4)-1
        if self.stochastic:
            gr_H_c = shocks.loc['gr_H',:].to_numpy()
        else :
            gr_H_c = np.zeros(4)
        gr_H = np.product([(1.0+gr_H_t + gr_H_c[q]) for q in range(4)])
        self.gr_H = gr_H-1
        # inflation
        infl_t = (1+self.base_inflrate[yr])**(1/4)-1
        if self.stochastic:
            infl_c = shocks.loc['infl',:].to_numpy()
        else :
            infl_c = np.zeros(4)
        infl = np.product([(1.0+infl_t + infl_c[q]) for q in range(4)])
        self.inflrate = infl-1
        # sp 500 returns
        sp500_t = (1+self.base_sp500[yr])**(1/4)-1
        if self.stochastic:
            sp500_c = shocks.loc['sp500',:].to_numpy()
        else :
            sp500_c = np.zeros(4)
        sp500 = np.product([(1.0+sp500_t + sp500_c[q]) for q in range(4)])
        self.sp500 = sp500-1
        # b1yr returns
        b1yr_t = self.base_b1yr[yr]
        if self.stochastic:
            b1yr_c = shocks.loc['b1yr',:].to_numpy()
        else :
            b1yr_c = np.zeros(4)
        b1yr = b1yr_t + np.mean(b1yr_c)
        self.b1yr = b1yr
        # b5yr returns
        b5yr_t = b1yr + self.base_b5yr_spread[yr]
        if self.stochastic:
            b5yr_c = shocks.loc['spread5yr',:].to_numpy()
        else :
            b5yr_c = np.zeros(4)
        b5yr = b5yr_t + np.mean(b5yr_c)
        self.b5yr = b5yr
        # b10yr returns
        b10yr_t = b5yr + self.base_b10yr_spread[yr]
        if self.stochastic:
            b10yr_c = shocks.loc['spread10yr',:].to_numpy()
        else :
            b10yr_c = np.zeros(4)
        b10yr = b10yr_t + np.mean(b10yr_c)
        self.b10yr = b10yr
        # b30yr returns
        b30yr_t = b10yr + self.base_b30yr_spread[yr]
        if self.stochastic:
            b30yr_c = shocks.loc['spread30yr',:].to_numpy()
        else :
            b30yr_c = np.zeros(4)
        b30yr = b30yr_t + np.mean(b30yr_c)
        self.b30yr = b30yr
        return

    def grow(self,yr,pop,eco):
        # generate shocks
        self.update_rates(yr,eco,pop)
        # compute population
        N = pop.sum()
        self.gr_N = N/self.N-1
        self.N = N
        # compute employment
        E = pop.multiply(eco['emp'],fill_value=0.0).sum()
        self.gr_E = E/self.E-1
        self.E = E
        # compute total hours worked
        self.H *= (1+self.gr_H)
        # Employment
        self.E = pop.multiply(eco['emp'],fill_value=0.0).sum()
        # create new potentiel and actual GDP
        self.Yp *= (1.0 + self.gr_H_p + self.base_gr_YperH[yr] + self.inflrate)
        self.Y *= (1.0 + self.gr_H + self.gr_YperH + self.inflrate)
        gr_Y = self.gr_H + self.gr_YperH + self.inflrate
        self.gr_Y = gr_Y
        self.gr_Yp = self.gr_H_p + self.base_gr_YperH[yr] + self.inflrate
        # wage growth
        self.gr_wage = self.gr_Y - self.gr_H
        self.gr_wage_p = self.gr_Yp - self.gr_H_p
        # keep in table
        self.to_aggr(yr)
        return
    def to_aggr(self,yr):
        self.aggr.loc[yr,'Y'] = self.Y
        self.aggr.loc[yr,'Yp'] = self.Yp
        self.aggr.loc[yr,'N'] = self.N
        self.aggr.loc[yr,'H'] = self.H
        self.aggr.loc[yr,'E'] = self.E
        self.aggr.loc[yr,'gr_wage'] = self.gr_wage
        self.aggr.loc[yr,'gr_wage_p'] = self.gr_wage_p
        self.aggr.loc[yr,'infl'] = self.inflrate
        self.aggr.loc[yr,'YperH'] = self.Y/self.H
        self.aggr.loc[yr,'sp500'] = self.sp500
        self.aggr.loc[yr,'b1yr'] = self.b1yr
        self.aggr.loc[yr,'b5yr'] = self.b5yr
        self.aggr.loc[yr,'b10yr'] = self.b10yr
        self.aggr.loc[yr,'b30yr'] = self.b30yr
        self.aggr.loc[yr,'gr_Y'] = self.gr_Y
        self.aggr.loc[yr,'gr_Yp'] = self.gr_Yp
        self.aggr.loc[yr,'gr_H'] = self.gr_H
        self.aggr.loc[yr,'gr_YperH'] = self.gr_YperH
        self.aggr.loc[yr,'gr_YperH_p'] = self.gr_YperH_p
        self.aggr.loc[yr,'gr_N'] = self.gr_N
        self.aggr.loc[yr,'gr_E'] = self.gr_E
        return
