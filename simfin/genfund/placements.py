import numpy as np
import pandas as pd
from simfin.tools import account
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class placements(account):
    '''
    Classe permettant de produire et d'intégrer au fond des génération les revenus de placement du FDG
    '''
    def __init__(self,start_value,e_trend=0.0,e_cycle=0.0,start_yr=2022):
        self.params = pd.read_csv(module_dir+'/genfund/params.csv')
        self.params=self.params.set_index(['variable']).transpose()
        self.future_value = pd.DataFrame()
        self.start_value = start_value
        self.value = self.start_value
        self.e_trend = e_trend
        self.e_cycle = e_cycle
        self.year = start_yr
        return
    def grow(self,macro,total_asset,market_value):
        fix_incomes = self.params['fix_incomes_share'].value * total_asset
        real_assets = self.params['real_assets_share'].value * total_asset
        shares = self.params['shares_share'].value * total_asset
        self.market_value = (fix_incomes*macro.return_fix_incomes + 
                      real_assets*macro.return_real_assets + 
                      shares*macro.return_shares)
        self.value = self.market_value * self.params['ratio_book_value_return'].value + self.capital_gain
        self.capital_gain = 0
        pass

    