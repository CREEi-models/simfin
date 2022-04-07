
from simfin.tools import account

class equalization(account):
    '''
    Classe permettant d'intégrer les revenus issus de la péréquation et de la formule de financement des territoires (FFT).

    Parameters
    ----------
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB réel.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    '''

    def grow(self,macro,pop,eco,others=None):
        rate = 1.0
        rate += macro.inflrate
        rate += self.e_trend * macro.gr_Yp + self.e_cycle * (macro.gr_Y-macro.gr_Yp) - macro.inflrate
        if rate < 1.03:
            rate = 1.03
        self.value *= rate
        return


    pass
