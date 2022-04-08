
from simfin.tools import account

class health_transfer(account):
    '''
    Classe permettant d'intégrer le transfert canadien en matière de santé (TCS).
    '''

    def grow(self,macro,pop,eco,others=None):
        rate = 1.0
        rate += macro.inflrate
        rate += self.e_trend * macro.gr_Yp + self.e_cycle * (macro.gr_Y-macro.gr_Yp) - macro.inflrate
        if rate < 1.03:
            rate = 1.03
        self.value *= rate
        return
