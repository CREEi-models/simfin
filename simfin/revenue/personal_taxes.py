from simfin.tools import account

class personal_taxes(account):
    '''
    Classe permettant d'intégrer l'impôt des particuliers.
    '''

    def set_align(self,pop,eco,tax):
        income = pop.multiply(eco['emp']*eco['earn_c']+eco['non_work_taxinc'],
                           fill_value=0.0)
        value  = income.multiply(tax['personal_tax_rate'],fill_value=0.0).sum()
        align = self.value/value
        tax['personal_tax_rate'] *= align
        self.core = self.value
        return tax
    def grow(self,macro,pop,eco,tax):
        earnings = pop.multiply(eco['emp']*eco['earn_c'],
                                fill_value=0.0)
        other_income = pop.multiply(eco['non_work_taxinc'],fill_value=0.0)
        share_earnings = earnings.sum()/(other_income.sum() + earnings.sum())
        income = earnings + other_income
        value = income.multiply(tax['personal_tax_rate'], fill_value=0.0).sum(
        )
        gr_pop = value/self.core-1.0
        self.core = value
        # earnings growth on trend at base YperH rate, get as residual from
        # potential GDP growth
        gr_trend_earn = macro.gr_YperH_p + macro.gr_H_p + \
                        macro.gr_YperH_p*macro.gr_H_p
        # cyclical is from shocks in output per worker and hours of work
        gr_cycle_earn = (macro.gr_YperH - macro.gr_YperH_p) + (macro.gr_H -
                                                       macro.gr_H_p)
        # other income grows with GDP
        gr_trend_other = macro.gr_YperH_p
        gr_cycle_other = macro.gr_Y - macro.gr_Yp
        gr_trend = share_earnings*gr_trend_earn + (1.0-share_earnings)*gr_trend_other
        gr_cycle = share_earnings*gr_cycle_earn + (1.0-share_earnings)*gr_cycle_other
        rate = 1.0 + macro.inflrate + gr_pop + self.e_trend*gr_trend + \
               self.e_cycle*gr_cycle
        self.value *= rate
        return
