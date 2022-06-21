import numpy as np
import pandas as pd
from simfin.tools import account


class gross_debt(account):
    '''
    Classe permettant de calculer la dette brutte.
    ''' 
    
    def grow(self,balance,immobilization,investments,others,delta_pension,delta_genfund,genfund_repay):
        # À modéliser les transferts de fonds du FDG vers la dette

        self.value += immobilization+investments+others-delta_pension-balance-delta_genfund-genfund_repay
        self.year+=1
        return 