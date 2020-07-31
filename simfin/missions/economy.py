from simfin.tools import account

class economy(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission Économie et environnement.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,igdp=True,ipop=False,iprice=False,others=None):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl
        if self.igdp:
            if macro.gr_Y>=0.0:
                rate += macro.gr_Y
        if self.ipop:
            rate += macro.gr_N
        self.value *= rate
        #print('Croissance de la mission économie : ',rate)
        return
