from simfin.tools import account 

class personal_credits(account):
    '''
    Classe permettant d'intégrer les crédits d'impôt remboursables des particuliers.

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
        self.start_value = value
        #self.value_family = 3197 #transfert soutien famille 2019
        #self.value_other = self.value - self.value_family
        #self.start_value_family = self.value_family
        #self.start_value_other = self.value - self.value_family
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return

    def set_align_family_credit(self,pop,eco):
        value_family = pop.multiply(eco['credit_famille']*(eco['emp']*eco['earn_c']+eco['taxinc']),fill_value=0.0).sum() # modif Bertrand
        align_family = self.value/value_family
        eco['credit_famille'] *= align_family
        #print('Facteur d\'alignement pour les credits famille : ', align_family)

        #Valeur pour les ensembles
        self.value_family = pop.multiply(eco['credit_famille']*(eco['emp']*eco['earn_c']+eco['taxinc']),fill_value=0.0).sum() # modif Bertrand
        self.start_value_family = self.value_family
        self.value_other = self.value - self.value_family
        self.start_value_other = self.value_other
        return
    
    def grow(self,macro,pop,eco,others=None):    
        """
        Fait croître la consommation par personne au rythme de l'inflation +
        1/alpha_L * la croissance de la TFP (A) (croissance des salaires).
        """
        igra = False
        rate = 1.0+macro.infl
        if igra == True:
            rate += 1/macro.g_pars['alpha_L']*macro.gr_A
        eco['credit_famille'] *= rate
        
        self.value_family = (pop.multiply(eco['credit_famille']*(eco['emp']*eco['earn_c']+eco['taxinc']),fill_value=0.0).sum()) # modif Bertrand

        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Y
        if self.ipop:
            rate += macro.gr_N
        self.value *= rate
        self.value_other *= rate

        self.value = self.value_family+self.value_other
        return 
