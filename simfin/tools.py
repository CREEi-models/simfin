
class account:
    '''
    Fonction permettant d'intégrer chaque composante des comptes publics.

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
        self.igdp = igdp
        self.iprice = iprice
        self.ipop = ipop
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.infl
        if self.igdp:
            rate += macro.gr_Y
        if self.ipop:
            rate += macro.gr_N
        self.value *= rate
        return
    def reset(self):
        self.value = self.start_value
        return

class accounts:
    '''
    Fonction permettant de colliger les comptes publics.
    '''
    def __init__(self,base,group_name,others=None):
        self.account_names = []
        for attr, value in base.items():
            self.account_names.append(attr)
            account_class = getattr(group_name,attr)
            setattr(self,attr,account_class(value,others=others))
        return
    def sum(self):
        return sum([getattr(self, acc).value for acc in self.account_names])
    def grow(self,macro,pop,eco,others=None):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(macro,pop,eco,others)
            setattr(self,acc_name,acc)
        return
    def reset(self):
        for acc_name in self.account_names:
            acc = getattr(self,acc_name)
            acc.reset()
            setattr(self,acc_name,acc)
        return
