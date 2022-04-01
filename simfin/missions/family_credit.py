from simfin.tools import account

class family_credit(account):
    '''
    Classe permettant d'intégrer les crédits d'impôt remboursables des particuliers.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    '''
    def set_align(self,pop,eco,tax):
        value = pop.multiply(tax['family_credits_rate']*(eco['emp']*eco[
            'earn_c']+eco['non_work_taxinc']),fill_value=0.0).sum()
        align = self.value/value
        tax['family_credits_rate'] *= align
        self.core = self.value
        return tax

    def grow(self,macro,pop,eco,tax):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A) (croissance des salaires).
        """
        value = pop.multiply(tax['family_credits_rate']*(eco[
                                                                       'emp']*eco[
            'earn_c']+eco['non_work_taxinc']),fill_value=0.0).sum()
        gr_pop = value/self.core-1.0
        self.core = value
        rate = 1.0 + macro.inflrate + gr_pop + self.e_trend * macro.gr_YperH_p \
               + \
               self.e_cycle * \
                                    (macro.gr_Y - macro.gr_Yp)
        self.value *= rate
        return
