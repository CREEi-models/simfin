import numpy as np
import pandas as pd
from simfin.tools import account


class annual_surplus(account):
    '''
    Classe permettant de calculer le surplus annuel.
    ''' 
    
    def grow(self,revenue,missions,federal,genfund,interest):
        self.value = revenue + federal - missions - interest
        self.year+=1
        return 