import numpy as np
import pandas as pd
from simfin.tools import account


class placements(account):
    '''
    Classe permettant de produire et d'intégrer au fond des génération les revenus de placement du FDG
    '''
   
    def grow(self,macro,total_asset,market_value):
        fix_incomes = .4 * total_asset
        real_assets = .15 * total_asset
        shares = .45 * total_asset
        self.value = total_asset*0.048 + self.capital_gain
        self.market_value = (fix_incomes*macro.return_fix_incomes + 
                      real_assets*macro.return_real_assets + 
                      shares*macro.return_shares)
        self.capital_gain = 0
        pass

    