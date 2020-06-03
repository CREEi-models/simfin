from simfin.tools import account

class family(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission de Soutien aux familles.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    ipop: boolean
        Switch pour intégrer ou non la croissance de la population.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,igdp=True,ipop=False,iprice=False):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return
    def set_sub_account(self,macro,pop,eco):
        self.value_credit_family = (pop.multiply(eco['credit_famille']*(eco['emp']*eco['earn_c']+eco['taxinc']),fill_value=0.0).sum()) # modif Bertrand
        self.value_kg = macro.data['family_kg']
        self.value_other = self.value-self.value_credit_family-self.value_kg

        self.start_value_credit_start = self.value_credit_family
        self.start_value_kg = self.value_kg
        self.start_value_other = self.value_other

        self.pop_04 = pop.loc[0:4].sum()
        self.start_pop_04 = self.pop_04
    def grow(self,macro,pop,eco):
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A) (croissance des salaires).
        """
        igra = True

        #credit
        rate = 1.0+macro.infl
        #if igra == True:
        #    rate += 1/macro.g_pars['alpha_L']*macro.gr_A
        eco['credit_famille'] *= rate
        
        self.value_credit_family = (pop.multiply(eco['credit_famille']*(eco['emp']*eco['earn_c']+eco['taxinc']),fill_value=0.0).sum()) # modif Bertrand

        #kindergarden
        pop_04 = pop.loc[0:4].sum()
        rate = 1.0 + macro.infl
        rate += (pop_04-self.pop_04)/self.pop_04

        if igra == True:
            rate += 1/macro.g_pars['alpha_L']*macro.gr_A
        self.value_kg *= rate
        self.pop_04 = pop_04

        #other
        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Y
        if self.ipop:
            rate += macro.gr_N
        self.value_other *= rate

        self.value = self.value_credit_family+self.value_kg+self.value_other
        return
