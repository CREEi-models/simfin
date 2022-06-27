import numpy as np
import pandas as pd
from simfin.tools import account


class miscellaneous_income(account):
    '''
    Classe permettant d'intégré au fond des génération les revenus provenant des biens non réclamés.
    '''
    def grow(self,macro,pop,eco,tax):
        rate = 1.0 + macro.inflrate + self.e_trend * (macro.gr_Yp -
                    macro.inflrate) + self.e_cycle * (macro.gr_Y - macro.gr_Yp)
        # add other components to growth here
        # apply growth
        if self.year in self.future_value:
            self.value = self.future_value[self.year]+self.value*(self.e_cycle * (macro.gr_Y - macro.gr_Yp))
        else : self.value *= rate
        self.year+=1
        return     
    
    pass