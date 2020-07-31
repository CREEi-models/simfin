
from simfin.tools import account

class consumption(account):
    '''
    Classe permettant d'intégrer les taxes à la consommation.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.

    '''
    def set_align(self,pop,eco):
        self.igdp = False
        value  = (pop.multiply(eco['cons']*eco['cons_taxes'],fill_value=0.0).sum())
        self.align = self.value/value
        #print('alignment factor for consommation tax : ', self.align)
        return

    def grow(self,macro,pop,eco,others=None):
        self.value = (pop.multiply(eco['cons']*eco['cons_taxes'],fill_value=0.0).sum())*self.align
        return
    pass
