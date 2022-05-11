from simfin.tools import accounts
import numpy as np
class collector(accounts):
    '''
    Fonction permettant de colliger les revenus qui abondent le Fonds des générations.

    Parameters
    ----------
    init_balance: float
        Montant du stock du Fonds des générations l'année d'initialisation du modèle.
    '''

    def __init__(self,base,group_name,others=None,start_yr=2022):
        self.account_names = []

        for i in base.index:
            self.account_names.append(i)
            account_class = getattr(group_name,i)
            setattr(self,i,account_class(base.loc[i,'start_value'],base.loc[
                i,'e_trend'],base.loc[i,'e_cycle'],start_yr)) 
        return
    
    ''' 
    def __init__(self,init_balance):
        self.balance = init_balance
        self.init_balance = init_balance
        rates = pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='Returns')
        self.rate = rates.set_index('year').mean()['genfund_return']
        self.strategy= pd.read_excel(module_dir+'/params/historical_accounts.xlsx',sheet_name='GenFundContrib')
        self.strategy = self.strategy.set_index('year')
        self.last_yr = self.strategy.index[-1]
        self.repay = 0.0
        self.rate_fdg = 1.0
        return
    def returns(self):
        return self.rate * self.balance
    def make_contrib(self,year,returns):
        rate=self.rate_fdg
        if year<=self.last_yr:
            contrib = self.strategy.loc[year,'contrib']
        else :
            contrib = 0.0
        self.contrib = contrib
        if returns==None:
            self.contrib = (contrib + self.returns()) * rate
        else :
            self.contrib = (contrib + returns) * rate
        return
    def grow(self,macro,repay=0.0,returns=None):
        self.make_contrib(macro.year,returns)
        balance_old = self.balance
        self.balance = self.balance + self.contrib
        if macro.year>self.last_yr:
            repay += self.balance
        self.balance -= repay
        self.balance_change= self.balance - balance_old
        self.repay = repay
        return
    def reset(self):
        self.balance = self.init_balance
        return
    '''