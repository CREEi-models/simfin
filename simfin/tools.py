import pandas as pd

class account:
    '''
    Fonction permettant d'intégrer chaque composante des comptes publics.
    '''
    def __init__(self,start_value,e_trend=0.0,e_cycle=0.0):
        self.start_value = start_value
        self.value = self.start_value
        self.e_trend = e_trend
        self.e_cycle = e_cycle
        return
    def grow(self,macro,pop,eco,tax):
        rate = 1.0 + macro.inflrate + self.e_trend * (macro.gr_Yp -
                    macro.inflrate) + self.e_cycle * (macro.gr_Y - macro.gr_Yp)
        # add other components to growth here
        # apply growth
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
        for i in base.index:
            self.account_names.append(i)
            account_class = getattr(group_name,i)
            setattr(self,i,account_class(base.loc[i,'start_value'],base.loc[
                i,'e_trend'],base.loc[i,'e_cycle']))
        return
    def sum(self):
        return sum([getattr(self, acc).value for acc in self.account_names])
    def init_report(self,start_yr):
        self.report = pd.DataFrame(index=self.account_names,columns=[start_yr])
    def report_back(self,yr):
        data = [getattr(self, acc).value for acc in self.account_names]
        self.report[yr] = data
        return
    def grow(self,macro,pop,eco,tax):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(macro,pop,eco,tax)
            setattr(self,acc_name,acc)
        return
    def reset(self):
        for acc_name in self.account_names:
            acc = getattr(self,acc_name)
            acc.reset()
            setattr(self,acc_name,acc)
        return
