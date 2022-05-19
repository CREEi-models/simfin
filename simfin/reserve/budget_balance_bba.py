import numpy as np
import pandas as pd
from simfin.tools import account


class budget_balance_bba(account):
    '''
    Classe permettant de calculer le solde budgétaire au sens de la loi sur l'équilibre budgétaire.
    ''' 
    
    def grow(self,balance,reserve):
        
        if balance<0:
            withdraw = min(-balance,reserve)
        else:
            withdraw = 0

        self.value = balance + withdraw
         
        self.year+=1
        return 