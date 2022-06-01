import numpy as np
import pandas as pd
from simfin.tools import account


class budget_balance(account):
    '''
    Classe permettant de calculer le surplus annuel avant réserve de stabilisation.
    ''' 
    
    def grow(self,revenue,missions,federal,genfund,interest):
        self.value = revenue + federal - missions - interest - genfund
        self.year+=1
        return 