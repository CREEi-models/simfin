
from simfin.tools import account

class consumption(account):
    '''
    Classe permettant d'intégrer les taxes à la consommation.
    '''
    def set_align(self,pop,eco,tax):
        value  = (pop.multiply(eco['cons']*tax['cons_tax_rate'],
                               fill_value=0.0).sum())
        align = self.value/value
        tax['cons_tax_rate'] *= align
        self.core = self.value
        return tax

    def grow(self,macro,pop,eco,tax):
        # growth from pop and aging
        cons = (pop.multiply(eco['cons']*tax['cons_tax_rate'],
                             fill_value=0.0).sum())
        gr_pop = cons/self.core - 1
        self.core = cons
        # growth with inflation, GDP trend and cycle
        rate = 1.0 + macro.inflrate + gr_pop + self.e_trend * \
               macro.gr_YperH_p \
               + self.e_cycle * \
               (macro.gr_Y - macro.gr_Yp)
        # apply growth
        #print(macro.inflrate, (
        #        macro.gr_Yp - macro.inflrate - macro.gr_H_p), (macro.gr_Y -
        #                                                       macro.gr_Yp),
        #      gr_pop)
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        else : self.value *= rate
        self.year+=1
        return
