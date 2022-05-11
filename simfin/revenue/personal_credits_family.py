from simfin.tools import account

class personal_credits_family(account):
    '''
    Classe permettant d'intégrer les crédits d'impôt remboursables des particuliers.
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
        Fait croître la consommation par personne au rythme de l'inflation et des salaires
        """
        value = pop.multiply(tax['family_credits_rate']*(eco[
                                                                       'emp']*eco[
            'earn_c']+eco['non_work_taxinc']),fill_value=0.0).sum()
        gr_pop = value/self.core-1.0
        self.core = value
        rate = 1.0 + gr_pop + self.e_trend * macro.gr_wage_p + self.e_cycle * (macro.gr_wage-macro.gr_wage_p)
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        else : self.value *= rate
        self.year+=1
        return
