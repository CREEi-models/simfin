import os
import pandas as pd
from simfin.tools import account
module_dir = os.path.dirname(os.path.dirname(__file__))

class additional_accounts(account):
    '''
    Classe permettant d'intégrer les revenus autonomes additionnels.
    '''

    def grow(self,macro,pop,eco,tax):
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        else : self.value = 0
        self.year+=1
        return

    pass
