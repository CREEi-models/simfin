import numpy as np
from simfin.tools import account
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector:
    '''
    Fonction permettant de colliger la dette liée aux pensions.

    Parameters
    ----------
    init_balance: float
        Montant du stock de la dette du système de retraite l'année d'initialisation du modèle.
    '''
    def __init__(self,init_liabilities,init_assets,init_actuarial_changes,
                 init_new_liabilities,init_paid_liabilities):

        """
        # predicted_balance   = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='pension_balance')
        # predicted_interests = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='pension_debt_service')
        # self.predicted_balance   = predicted_balance.set_index('year')
        # self.predicted_interests = predicted_interests.set_index('year')
        # self.balance  = init_balance
        # self.year_last = self.predicted_balance.index.max()
        """
        # on charge les stocks

        self.init_liabilities = init_liabilities
        self.init_assets      = init_assets

        self.liabilities       = init_liabilities
        self.assets            = init_assets
        self.actuarial_changes = init_actuarial_changes
        # on calcule la balance
        self.balance           = self.liabilities - self.assets + self.actuarial_changes

        # on charge les hypothèses de croissances
        self.hypothesis = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='pension_hypo')
        self.hypothesis  = self.hypothesis.set_index('vars')

        # le taux d'intérêt est de 6.5% nominal (inclure un taux réel demanderait de réactualiser)
        self.rate             = self.hypothesis.loc['pension - interest','value']
        self.new_liabilities  = init_new_liabilities
        self.paid_liabilities = init_paid_liabilities

        self.update_new_liabilities  = self.hypothesis.loc['pension - new liabilities','value']
        self.update_paid_liabilities = self.hypothesis.loc['pension - paid liabilities','value']
        self.others                  = self.hypothesis.loc['pension - others','value']

        return

    def compute_interests(self):
        self.interests = (self.liabilities-self.assets)*self.rate
        return

    def grow(self,macro,year,fix_after2025=True):
        """
        year_i = min(year,self.year_last)
        self.balance_change = self.predicted_balance.loc[year_i,'balance']-self.balance
        self.balance   =  self.predicted_balance.loc[year_i,'balance']
        """
        """
        NB marche à partir de 2019, montant initial de new liabilities ... devrait être ajusté si on commence plus tôt
        """
        if fix_after2025 == True and year > 2025:
            # à partir de 2026, passif reste à son niveau de 2025
            # et actif = passif
            self.liabilities = self.liabilities + self.actuarial_changes
            self.assets      = self.liabilities

            new_balance = self.liabilities - self.assets
            self.balance_change = new_balance-self.balance
            self.balance = new_balance

        else:
            self.update_new_liabilities  *= (1+macro.infl)
            self.update_paid_liabilities *= (1+macro.infl)
            self.others           *= (1+macro.infl)
            self.new_liabilities  += self.update_new_liabilities
            self.paid_liabilities += self.update_paid_liabilities

            self.liabilities = self.liabilities*(1+self.rate)+self.new_liabilities -self.paid_liabilities+self.others
            self.assets = self.assets*(1+self.rate)
            if year == 2020:
                self.assets = self.assets + 1500

            new_balance = self.liabilities - self.assets + self.actuarial_changes
            self.balance_change = new_balance-self.balance
            self.balance = new_balance

        return


    def reset(self):
        self.liabilities = self.init_liabilities
        self.assets      = self.init_assets
        self.balance     = self.liabilities - self.assets + self.actuarial_changes

        return
