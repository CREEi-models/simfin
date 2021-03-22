from simfin.tools import account

class justice(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission Gouverne et Justice.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    '''
    def __init__(self,value,igdp=True,ipop=False,others=None):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.ipop = ipop
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Yp
        if self.ipop:
            rate += macro.gr_N
        self.value *= rate
        return
