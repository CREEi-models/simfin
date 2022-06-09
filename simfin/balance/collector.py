import numpy as np
from simfin.tools import accounts
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector(accounts):
    '''
    Fonction permettant de colliger les surplus annuel, du solde budgétaire.

    '''
    def grow(self,revenue,missions,federal,genfund,interest):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(revenue,missions,federal,genfund,interest)
            setattr(self,acc_name,acc)
        return