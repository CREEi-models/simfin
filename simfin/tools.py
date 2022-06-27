import pandas as pd
import numpy as np
class account:
    '''
    Fonction permettant d'intégrer chaque composante des comptes publics.
    '''
    def __init__(self,start_value,e_trend=0.0,e_cycle=0.0,start_yr=2022):
        self.future_value = pd.DataFrame()
        self.start_value = start_value
        self.value = self.start_value
        self.e_trend = e_trend
        self.e_cycle = e_cycle
        self.year = start_yr
        return
    def grow(self,macro,pop,eco,tax):
        rate = 1.0 + macro.inflrate + self.e_trend * (macro.gr_Yp -
                    macro.inflrate) + self.e_cycle * (macro.gr_Y - macro.gr_Yp)
        # add other components to growth here
        # apply growth
        if self.year in self.future_value:
            self.value = self.future_value[self.year]+self.value*(self.e_cycle * (macro.gr_Y - macro.gr_Yp))
        else : self.value *= rate
        self.year+=1
        return  
        
    def reset(self):
        self.value = self.start_value
        return

class accounts:
    '''
    Fonction permettant de colliger les comptes publics.
    '''
    def __init__(self,base,group_name,others=None,start_yr=2022):
        self.account_names = []
        for i in base.index:
            self.account_names.append(i)
            account_class = getattr(group_name,i)
            setattr(self,i,account_class(base.loc[i,'start_value'],base.loc[
                i,'e_trend'],base.loc[i,'e_cycle'],start_yr))
        return
    def set_future_value(self,base,group_name,start_yr):
        self.account_names = []
        for i in base.index:
            self.account_names.append(i)
            account_class = getattr(group_name,i)
            if np.isnan(base.loc[i,start_yr]):
                continue
            max_year = start_yr
            j = 0
            while True:
                if start_yr+j in base:
                    if not np.isnan(base.loc[i,start_yr+j]):
                        max_year = start_yr+j
                        j+=1
                    else: break
                else: break
            setattr(account_class,'future_value',base.loc[i,range(start_yr,max_year+1)]) 
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
