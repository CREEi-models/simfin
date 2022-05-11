import numpy as np
import pandas as pd
from simfin.tools import account


class hydro_additionnal(account):
    '''
    Classe permettant d'intégré au fond des génération les revenus provenant de la contribution additionel d'Hydro-Québec.
    '''
    def grow(self,macro,pop,eco,others=None):
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        self.year+=1
        return     
    
    pass