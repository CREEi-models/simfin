import numpy as np

import numpy as np
from simfin.tools import account
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector:
    '''
    Fonction permettant de colliger les revenus qui abondent la réserve de stabilisation.

    Parameters
    ----------
    init_balance: float
        Montant du stock sur la réserve de stabilisation l'année d'initialisation du modèle.
    max_rate: float
        Part maximale de la réserve de stabilisation dans les dépenses totales du gouvernement. Au dessus de max_rate, les surplus générés sont affectés à la dette.
    '''
    def __init__(self,init_balance,max_rate=0.15):
        self.balance = init_balance
        self.init_balance = init_balance
        self.max_rate = max_rate
        return
    def grow(self, surplus, spending):
        change = surplus
        self.balance = self.balance + change
        max_balance = self.max_rate * spending
        repay = 0.0
        if self.balance > max_balance:
            repay = max(self.balance - max_balance,0.0)
            self.balance = max_balance
        if self.balance < 0.0:
            repay = self.balance
            self.balance = 0.0
        return repay
    def reset(self):
        self.balance = self.init_balance
        return
