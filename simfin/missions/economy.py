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
    def __init__(self,value,igdp=True,ipop=False,iprice=False):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return
