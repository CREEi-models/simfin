
from simfin.tools import account

class health_transfer(account):
    '''
    Classe permettant d'intégrer le transfert canadien en matière de santé (TCS).

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    '''

    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Yp
        if self.ipop:
            rate += macro.gr_N
        if rate < 1.03:
            rate = 1.03
        self.value *= rate
        return

    pass
