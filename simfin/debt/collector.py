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
   '''
    def __init__(self,init_balance,base):
        self.balance = init_balance
        self.init_balance = init_balance
        self.account_names = []
        for attr, value in base.items():
            self.account_names.append(attr)
            setattr(self,attr,account(value,igdp=True))
        self.new_borrow = 0.0
        self.repay = 0.0
        rates = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='Returns')
        self.rate = rates.set_index('year').mean()['debt_interest']
        return
    def service(self):
        return self.rate * self.balance
    def borrowing(self,amount):
        self.new_borrow = amount
        return
    def repaying(self,amount):
        self.repay = amount
        return
    def grow(self,macro,pop,eco):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            if macro.year > macro.start_yr:
                acc.grow(macro,pop,eco)
            setattr(self,acc_name,acc)
        self.balance = (self.balance + self.debt_borrow.value + self.new_borrow
                        - self.repay - self.debt_depr_fund.value + self.debt_ppp.value)
        return
    def reset(self):
        for acc_name in self.account_names:
            acc = getattr(self,acc_name)
            acc.reset()
            setattr(self,acc_name,acc)
        self.new_borrow = 0.0
        self.repay = 0.0
        self.balance = self.init_balance
        return
