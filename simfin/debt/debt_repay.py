import numpy as np
import pandas as pd
from simfin.tools import account


class debt_repay(account):
    '''
    Classe permettant de calculer les paiements sur la dette.
    ''' 
    
    def grow(self,balance,delta_placements,delta_others,delta_fixed_assets,delta_pension,delta_genfund,genfund_repay):
        # À ajouter les transferts de fonds du FDG vers la dette

        self.value = max(0,balance) + genfund_repay
        self.year+=1
        return 