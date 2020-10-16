from simfin.tools import account

class corporate_credits(account):
    '''
    Classe permettant d'intégrer les crédits d'impôt remboursables des sociétés.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,igdp=False,ipop=False,iprice=False,others=None):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl + macro.gr_Y 
        self.value *= rate
        return
