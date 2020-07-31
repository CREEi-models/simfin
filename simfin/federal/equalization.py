
from simfin.tools import account

class equalization(account):
    '''
    Classe permettant d'intégrer les revenus issus de la péréquation et de la formule de financement des territoires (FFT).

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Y
        if self.ipop:
            rate += macro.gr_N
        if rate < 1.03:
            rate = 1.03
        self.value *= rate
        #print('rate for  equalization : ',rate)
        return
