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
    def set_sub_account(self,macro,pop):
        self.pop_04 = pop.loc[0:4].sum()
        self.start_pop_04 = self.pop_04

    def grow(self,macro,pop,eco,tax):
        """
        Fait croître les dépenses des services de garde au rythme des salaires nominaux (salaires réels + inflation) + au rythme de de la croissance de la population des 0 à 4 ans.
        """
        pop_04 = pop.loc[0:4].sum()
        gr_pop = (pop_04-self.pop_04)/self.pop_04
        self.pop_04 = pop_04
        rate = 1.0 + gr_pop + self.e_trend * macro.gr_wage_p + self.e_cycle * (macro.gr_wage-macro.gr_wage_p)
        self.value *= rate
        return
