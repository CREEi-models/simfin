
from simfin.tools import account

class health_transfer(account):
    '''
    Classe permettant d'intégrer le transfert canadien en matière de santé (TCS).

    Parameters
    ----------
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    igdp: boolean
        Switch pour intégrer ou non la croissance potentielle du PIB réel.
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
            rate += macro.infl
        if self.igdp:
            rate += macro.gr_Yp
        if self.ipop:
            rate += macro.gr_N
        if rate < 1.03:
            rate = 1.03
        self.value *= rate
        return


    pass
