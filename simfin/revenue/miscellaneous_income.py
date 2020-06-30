from simfin.tools import account

class miscellaneous_income(account):
    '''
    Classe permettant d'intégrer toutes les revenus divers (dont une partie sont les revenus de placement du FDG)

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
        if others !=None:
            self.gfundinc_init   = others['gfund_inc_init']
            self.gfundinc        = others['gfund_inc_init']
        else:
            self.gfundinc_init   = 0.0
            self.gfundinc        = 0.0

        self.nogfundinc_init = self.value - self.gfundinc_init
        self.nogfundinc      = self.value - self.gfundinc_init
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return

    def grow(self,macro,pop,eco,others):
        rate = 1.0
        if self.iprice:
            rate += macro.infl
        if self.igdp:
            rate += macro.gr_Y
        self.gfundinc   = others['gfund_inc']
        self.nogfundinc *= rate
        self.value       = self.nogfundinc + self.gfundinc
        return

    def reset(self):
        self.nogfundinc = self.nogfundinc_init
        self.gfundinc    = self.gfundinc_init
        self.value       = self.nogfundinc + self.gfundinc
        return

    #pass
