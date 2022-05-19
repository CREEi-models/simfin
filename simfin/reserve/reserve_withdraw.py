import numpy as np
import pandas as pd
from simfin.tools import account


class reserve_withdraw(account):
    '''
    Classe permettant de calculer le retrait de la réserve de stabilisation.
    ''' 
    
    def grow(self,balance,reserve):
        if balance<0:
            self.value = min(-balance,reserve)
        else:
            self.value = 0
        self.year+=1
        return 