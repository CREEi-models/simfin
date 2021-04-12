from simfin.tools import account

class personal_taxes(account):
    '''
    Classe permettant d'intégrer l'impôt des particuliers.
    '''

    def set_align(self,pop,eco):
        earnings = pop.multiply(eco['emp']*eco['earn_c']+eco['taxinc'],fill_value=0.0)
        value  = earnings.multiply(eco['personal_taxes'],fill_value=0.0).sum()
        self.align = self.value/value
        return

    def grow(self,macro,pop,eco,others):
        earnings = pop.multiply(eco['emp']*eco['earn_c']+eco['taxinc'],fill_value=0.0)
        self.value = (earnings.multiply(eco['personal_taxes'],fill_value=0.0).sum())*self.align
        return
    pass
