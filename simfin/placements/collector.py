import numpy as np
from simfin.tools import account
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector:
    '''
    Fonction permettant de colliger les placements, prêts et avances ; et les autres facteurs

    Parameters
    ----------
    init_balance: float
        Montant du stock des placements, prêts et avances ; et des autres facteurs
    '''

    def __init__(self,init_balance):
        self.init_balance = init_balance
        self.balance      = init_balance
        investment_pred    = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='investment')
        self.investment_pred  = investment_pred.set_index('year')
        self.year_last    = self.investment_pred.index.max()
        return
    def grow(self,year,gdp):
        # fait croître la balance
        # + génère les nouveaux investissements dans placements... et autres facteurs
        year_i = min(year,self.year_last)
        self.net_placements    = gdp* self.investment_pred.loc[year_i,'placements']
        self.net_other_factors = gdp* self.investment_pred.loc[year_i,'other factors']
        self.balance += self.net_placements + self.net_other_factors
        return
    def reset(self):
        self.balance = self.init_balance
        return
