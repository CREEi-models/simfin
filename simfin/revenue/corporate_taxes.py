from simfin.tools import account

class corporate_taxes(account):
    '''
    Classe permettant d'intégrer l’impôt des sociétés.
    '''
    def __init__(self,value,others=None):
        self.value = value
        self.start_value = value
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl + macro.gr_Y
        self.value *= rate
        return
