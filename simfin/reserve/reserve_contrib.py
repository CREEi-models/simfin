import numpy as np
import pandas as pd
from simfin.tools import account


class reserve_contrib(account):
    '''
    Classe permettant de calculer la contribution à la réserve de stabilisation.
    ''' 
    
    def grow(self,balance,reserve):
        if balance>0:
            self.value = balance
        else:
            self.value = 0
        
        self.year+=1
        return 