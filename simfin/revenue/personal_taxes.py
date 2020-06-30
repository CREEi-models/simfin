from simfin.tools import account

class personal_taxes(account):
    '''
    Classe permettant d'intégrer l'impôt des particuliers.

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
        #work_earnings = pop.multiply(eco['emp']*eco['earn_c'],fill_value=0.0)
        #non_work_earnings = pop.multiply(eco['taxinc'],fill_value=0.0)
        #earnings = work_earnings + non_work_earnings
        #print('non_work/earnings :', non_work_earnings.sum()/earnings.sum() )
        earnings = pop.multiply(eco['emp']*eco['earn_c']+eco['taxinc'],fill_value=0.0)
        value  = earnings.multiply(eco['personal_taxes'],fill_value=0.0).sum()
        self.align = self.value/value
        #print('alignment factor for personal tax : ', self.align)
        return

    def grow(self,macro,pop,eco,others):
        #work_earnings = pop.multiply(eco['emp']*eco['earn_c'],fill_value=0.0).sum()
        #non_work_earnings = pop.multiply(eco['taxinc'],fill_value=0.0).sum()
        #print('non_work/earnings :', non_work_earnings/(work_earnings+non_work_earnings) )
        earnings = pop.multiply(eco['emp']*eco['earn_c']+eco['taxinc'],fill_value=0.0)
        self.value = (earnings.multiply(eco['personal_taxes'],fill_value=0.0).sum())*self.align
        return
    pass
