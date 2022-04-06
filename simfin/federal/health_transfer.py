
from simfin.tools import account

class health_transfer(account):
    '''
    Classe permettant d'intégrer le transfert canadien en matière de santé (TCS).

    Parameters
    ----------
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB réel.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    '''
    def __init__(self,value,iprice=True,igdp=True,ipop=False,others=None):
        self.value = value
        self.iprice = iprice
        self.igdp = igdp
        self.ipop = ipop
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0
        if self.iprice:
            rate += macro.inflrate
        if self.igdp:
            rate += self.e_trend * macro.gr_Yp + self.e_cycle * (macro.gr_Y-macro.gr_Yp) - macro.inflrate
        if self.ipop:
            rate += macro.gr_N
        #if rate < 1.03:
        #    rate = 1.03
        self.value *= rate
        return


    pass
