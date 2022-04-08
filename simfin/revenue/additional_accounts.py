import os
import pandas as pd
from simfin.tools import account
module_dir = os.path.dirname(os.path.dirname(__file__))

class additional_accounts(account):
    '''
    Classe permettant d'intégrer les autres transferts fédéraux.
    '''

    def grow(self,macro,pop,eco,others=None):
        self.value = pd.read_csv(module_dir+'/params/additional_accounts.csv', index_col=0, sep = ';').loc['revenue',str(macro.yr)]
        return
