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
    '''
    def __init__(self,init_balance):
        self.balance = init_balance
        self.init_balance = init_balance
        return
    def grow(self, surplus):
        change = surplus
        self.balance = self.balance + change
        return
    def reset(self):
        self.balance = self.init_balance
        return
