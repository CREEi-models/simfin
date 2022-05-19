import numpy as np
import pandas as pd
from simfin.tools import account


class reserve_balance(account):
    '''
    Classe permettant de calculer le montant de la réserve de stabilisation.
    ''' 
    
    def grow(self,balance,reserve):
        self.value += balance
         
        self.year+=1
        return 