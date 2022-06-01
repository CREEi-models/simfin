import numpy as np

import numpy as np
from simfin.tools import accounts
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector(accounts):
    '''
    Fonction permettant de colliger la réserve de stabilisation et le solde après réserve de stabilisation.
    '''

    def grow(self,balance,reserve):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(balance,reserve)
            setattr(self,acc_name,acc)
        return
    
