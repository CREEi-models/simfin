from simfin.tools import account

class other_transfers(account):
    '''
    Classe permettant d'intégrer les autres transferts fédéraux.
    '''

    def grow(self,macro,pop,eco,others=None):
        rate = 1.0
        rate += macro.inflrate
        rate += self.e_trend * macro.gr_Yp + self.e_cycle * (macro.gr_Y-macro.gr_Yp) - macro.inflrate
        if rate < 1.03:
            rate = 1.03
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        else : self.value *= rate
        self.year+=1
        return
