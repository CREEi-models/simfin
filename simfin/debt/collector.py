import numpy as np
from simfin.tools import account
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector:
    '''
    Fonction permettant de colliger le déficit public dans la dette du gouvernement provincial.

    Parameters
    ----------
    init_balance: float
        Montant de la dette publique du gouvernement provincial pour l'année d'initialisation du modèle.
    base: float
        Collecte tous les items qui viennent abonder la dette publique.

    NB: dette ici = dette avant gains de change - emprunts réalisés par anticipation
   '''
    def __init__(self,init_balance):
        self.balance = init_balance
        self.init_balance = init_balance
        self.account_names = []
        rates = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='Returns')
        self.rate = 0.0379
        return
    def debt_interest(self):
        return self.rate * self.balance
    def grow(self,macro,delta_placements,delta_others,delta_fixed_assets,budget_balance,delta_pension,repay_genfund):
        if macro.year > macro.start_yr:
            self.balance += delta_placements+delta_others+delta_fixed_assets-delta_pension-budget_balance\
            -repay_genfund
        return
    def reset(self):
        self.balance = self.init_balance
        return
