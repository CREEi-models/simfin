import numpy as np
import pandas as pd
from simfin.tools import account


class direct_debt(account):
    '''
    Classe permettant de calculer la dette directe consolidée.
    ''' 
    
    def grow(self,balance,immobilization,investments,others_factors,delta_pension,delta_genfund,genfund_repay):
        # À ajouter les transferts de fonds du FDG vers la dette

        self.value += immobilization+investments+others_factors-balance-genfund_repay
        self.year+=1
        return 