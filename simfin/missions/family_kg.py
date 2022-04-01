from simfin.tools import account

class family_kg(account):
    '''
    Classe permettant d’intégrer les dépenses des services de garde (mission de Soutien aux familles).

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,igdp=True,ipop=False,others=None):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.ipop = ipop
        return

    def set_sub_account(self,macro,pop):
        self.pop_04 = pop.loc[0:4].sum()
        self.start_pop_04 = self.pop_04

    def grow(self,macro,pop,eco,tax):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A) (croissance des salaires).
        """
        pop_04 = pop.loc[0:4].sum()
        gr_pop = (pop_04-self.pop_04)/self.pop_04
        self.pop_04 = pop_04
        #rate += 1/macro.g_pars.loc['alpha_L',1]*macro.gr_A
        rate = 1.0 + macro.inflrate + gr_pop
        self.value *= rate
        return
