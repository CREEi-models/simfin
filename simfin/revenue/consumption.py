
from simfin.tools import account

class consumption(account):
    '''
    Classe permettant d'intégrer les taxes à la consommation.
    '''
    def set_align(self,pop,eco):
        value  = (pop.multiply(eco['cons']*eco['cons_taxes'],fill_value=0.0).sum())
        self.align = self.value/value
        return

    def grow(self,macro,pop,eco,others=None):
        self.value = (pop.multiply(eco['cons']*eco['cons_taxes'],fill_value=0.0).sum())*self.align
        return
    pass
