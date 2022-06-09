import numpy as np
from simfin.tools import accounts
import os
import pandas as pd
module_dir = os.path.dirname(os.path.dirname(__file__))

class collector(accounts):
    '''
    Fonction permettant de colliger le déficit public dans la dette du gouvernement provincial.
    '''
   
    def __init__(self,base,group_name,others=None,start_yr=2022):
        self.interest_value = 0.0     
        self.account_names = []     
        for i in base.index:
            self.account_names.append(i)
            account_class = getattr(group_name,i)
            setattr(self,i,account_class(base.loc[i,'start_value'],base.loc[
                i,'e_trend'],base.loc[i,'e_cycle'],start_yr))

        self.debt_structure = pd.read_excel(
            module_dir+'/debt/debt_structure.xlsx',
                                    sheet_name='data')
        self.debt_structure.set_index(['term','remaining_yr','type'],inplace=True)
        return
    
    def grow(self,balance,delta_placements,delta_others,delta_fixed_assets,delta_pension,delta_genfund,genfund_repay):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(balance,delta_placements,delta_others,delta_fixed_assets,delta_pension,delta_genfund,genfund_repay)
            setattr(self,acc_name,acc)
        return

    def interests(self,year):
        # besoin d'ajouter les intérets p/r aux pensions

        self.interests_value = (self.debt_structure[year-1].loc[:,:,'value'].multiply(self.debt_structure[year-1].loc[:,:,'rate'])).sum()
        #print(self.interests_value)
        return 

    def structure_update(self,macro,delta_direct_debt,year,share_1yr=0.1,share_5yr=0.1,share_10yr=0.70,share_30yr=0.1):
        loan_need = delta_direct_debt + self.debt_structure[year-1].loc[5,1,'value'] + self.debt_structure[year-1].loc[10,1,'value'] + self.debt_structure[year-1].loc[30,1,'value']

        self.debt_structure[year] = self.debt_structure.groupby(['term','type'])[year-1].shift(-1)
            
        self.debt_structure[year].loc[1,1,'value'] = loan_need*share_1yr
        self.debt_structure[year].loc[5,5,'value'] = loan_need*share_5yr
        self.debt_structure[year].loc[10,10,'value'] = loan_need*share_10yr
        self.debt_structure[year].loc[30,30,'value'] = loan_need*share_30yr

        self.debt_structure[year].loc[1,1,'rate'] = macro.aggr.loc[year,'b1yr']
        self.debt_structure[year].loc[5,5,'rate'] = macro.aggr.loc[year,'b5yr']
        self.debt_structure[year].loc[10,10,'rate'] = macro.aggr.loc[year,'b10yr']
        self.debt_structure[year].loc[30,30,'rate'] = macro.aggr.loc[year,'b30yr']
        return

    def init_report(self,start_yr):
        self.report = pd.DataFrame(index=[*self.account_names,"debt_interests"],columns=[start_yr])
    
    def report_back(self,yr):
        data = [getattr(self, acc).value for acc in self.account_names]
        data.append(self.interests_value)

        self.report[yr] = data
        return    
