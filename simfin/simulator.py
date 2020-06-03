import pandas as pd
import numpy as np
from simfin import revenue, macro, federal, missions, debt, genfund, reserve
import os
module_dir = os.path.dirname(os.path.dirname(__file__))
import functools


class simulator:
    """
    Classe principale pour contrôler le simulateur.

    Cette classe permet d'initialiser les paramètres et réaliser des simulations.

    Parameters
    ----------
    start_yr: int
        année de départ de la projection
    stop_yr: int
        année de fin de la projection
    """
    def __init__(self,start_report,stop_yr):
        if start_report>2019 :
            raise ValueError('Les statistiques doivent commencer entre 2006 et 2019')
        else:
            self.start_report = start_report
        self.start_yr = 2019
        self.stop_yr = stop_yr
        self.year = self.start_report
        self.maxyrs = self.stop_yr - self.start_report + 1
        self.macro = macro(self.start_yr)
        self.load_accounts()
        self.load_params()

        self.init_revenue()
        self.init_transfers()
        self.init_missions() #need to be after self.init_revenue()
        self.init_gfund()
        self.init_reserve()
        self.init_debt()
        return
    def load_accounts(self):
        """
        Fonction permettant de charger l'historique des comptes publics.

        L'historique des comptes publics a été comptabilisé pour la période 2006-2019. Cette fonction charge les valeurs des comptes publics et prépare le rapport sommaire (summary report) pour les résultats.

        """
        self.history = pd.read_excel(module_dir+'/simfin/params/historical_accounts.xlsx',sheet_name='Inputs')
        self.history = self.history.set_index('account')
        self.names = ['personal','corporate','consumption','other taxes','autonomous','federal transfers','total revenue','mission health','mission education','mission family','other missions','mission spending',
            'debt service','total spending','surplus','generation fund','fund contribution','net surplus',
            'reserve','debt','gross debt','gdp','debt-to-gdp','gdp growth','pop growth','emp growth']
        self.summary = pd.DataFrame(index=self.names,columns=[t for t in range(self.start_report,self.stop_yr)])
        return
    def load_params(self,file_pop='/simfin/params/simpop.pkl',file_profiles='/simfin/params/'):
        '''
        Fonction qui charge différents paramètres: a) la projection démographique, b) les statuts économiques par âge et c) les paramètres macroéconomiques.

        Keyword Arguments:
            file_pop {str} -- [fichier SimGen] (défaut: {'module_dir+/simfin/params/simpop.pkl'})
        '''

        if file_pop!='/simfin/params/simpop.pkl':
            self.pop = pd.read_pickle(file_pop)
        else :
            self.pop = pd.read_pickle(module_dir+file_pop)
        #self.eco_first = pd.read_pickle(module_dir+'/simfin/params/economic_outcomes.pkl')
        self.eco_first = pd.DataFrame(pd.read_pickle(module_dir+file_profiles+'emp.pkl'))
        earn_c = pd.read_pickle(module_dir+file_profiles+'earn_c.pkl')
        cons = pd.read_pickle(module_dir+file_profiles+'cons.pkl')
        hours_c = pd.read_pickle(module_dir+file_profiles+'hours_c.pkl')
        cons_taxes = pd.read_pickle(module_dir+file_profiles+'cons_taxes.pkl')
        non_work_taxinc = pd.read_pickle(module_dir+file_profiles+'non_work_taxinc.pkl')
        personal_taxes = pd.read_pickle(module_dir+file_profiles+'personal_taxes.pkl')
        family_credits = pd.read_pickle(module_dir+file_profiles+'credit_famille.pkl')

        #taxinc = pd.read_pickle(module_dir+'/simfin/params/personal_taxes.pkl')

        self.eco_first = (self.eco_first.merge(earn_c/1e6,left_index=True, right_index=True,how='outer').
                          merge(cons/1e6,left_index=True, right_index=True,how='outer').
                          merge(hours_c,left_index=True, right_index=True,how='outer').
                          merge(cons_taxes,left_index=True, right_index=True,how='outer').
                          merge(non_work_taxinc/1e6,left_index=True, right_index=True,how='outer').
                          merge(personal_taxes,left_index=True, right_index=True,how='outer').
                          merge(family_credits,left_index=True, right_index=True,how='outer').
                          fillna(value=0))

        self.eco = self.eco_first.copy()
        work_earnings = self.pop[self.start_yr].multiply(self.eco['emp']*self.eco['earn_c'],fill_value=0.0).sum()
        non_work_earnings = self.pop[self.start_yr].multiply(self.eco['taxinc'],fill_value=0.0).sum()
        earnings = work_earnings + non_work_earnings
        print('non_work/earnings :', non_work_earnings/earnings )

        self.macro.set_align_emp(self.pop[self.start_yr],self.eco)
        self.macro.set_align_cons(self.pop[self.start_yr],self.eco)
        return
    def init_revenue(self):
        """Fonction initialisation des revenues

        Fonction qui crée les comptes de revenus et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.

        """
        revenue_accounts = self.history.loc[:'other_taxes',self.start_yr]
        self.revenue = revenue.collector(revenue_accounts,revenue)
        self.revenue.consumption.set_align(self.pop[self.start_yr],self.eco)
        self.revenue.personal_taxes.set_align(self.pop[self.start_yr],self.eco)
        self.revenue.personal_credits.set_align_family_credit(self.pop[self.start_yr],self.eco)


        return
    def init_transfers(self):
        """Fonction initialisation des transfers fédéraux

        Fonction qui crée les comptes de transfers fédéraux et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        names = ['equalization','health_transfer','other_transfers']
        transfer_accounts = self.history.loc[names,self.start_yr]
        self.transfers = federal.collector(transfer_accounts,federal)
        return
    def init_missions(self):
        """Fonction initialisation des dépenses de missions

        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        names = ['economy','education','family','health','justice']
        mission_accounts = self.history.loc[names,self.start_yr]
        self.missions = missions.collector(mission_accounts,missions)
        self.missions.health.set_align(self.pop[self.start_yr])
        self.missions.education.set_align(self.pop[self.start_yr])
        self.missions.family.set_sub_account(self.macro,self.pop[self.start_yr],self.eco)
        return
    def init_debt(self):
        """Fonction initialisation des comptes de la dette publique.

        Fonction qui crée les comptes de dettes et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        names = ['debt_borrow','debt_depr_fund','debt_ppp','debt_pension','gross_debt_reduct']
        debt_accounts = self.history.loc[names,self.start_yr]
        balance_start = self.history.loc['debt_balance_start',self.start_yr]
        self.debt = debt.collector(balance_start,debt_accounts)
        return
    def init_gfund(self):
        """Fonction initialisation du fonds des générations.

        Fonction qui crée les comptes du fonds des générations et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        balance_start = self.history.loc['gfund_balance_start',self.start_yr]
        self.genfund = genfund.collector(balance_start)
        return
    def init_reserve(self):
        """Fonction initialisation de la réserve de stabilisation.

        Fonction qui crée les comptes de la réserve de stabilisation et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        balance_end = self.history.loc['reserve_balance_end',self.start_yr]
        self.reserve = reserve.collector(balance_end)
        
    def next(self):
        """Fonction de transition.

        Fonction qui permet de faire une transition, croissance économique et des comptes et fait la comptabilisation des comptes publics, mise-à-jour de la dette.
        """
        if self.year>self.start_yr:
            self.macro.emp(self.pop[self.year],self.eco)
            self.macro.pop(self.pop[self.year])
            self.macro.grow_cons(self.eco)
            self.macro.grow_work_earnings(self.eco)
            self.macro.grow_non_work_earnings(self.eco) # B. Achou
            self.macro.grow(self.year)
            self.revenue.grow(self.macro,self.pop[self.year],self.eco)
            self.transfers.grow(self.macro,self.pop[self.year],self.eco)
            self.missions.grow(self.macro,self.pop[self.year],self.eco)
        # revenue
        self.collect_revenue()
        # spending
        self.collect_spending()

        # surplus gen fund and reserves
        surplus = self.summary.loc['total revenue',self.year] - self.summary.loc['total spending',self.year]
        self.summary.loc['surplus',self.year] = surplus
        # special debt repayment (actual) from genfund before 2020
        repay = 0.0
        if self.year <= self.history.columns[-1]:
            repay += self.history.loc['debt_repay',self.year]
            #repay = self.genfund.grow(self.macro,repay,returns=self.history.loc['gfund_returns',self.year])
        else :
            repay = self.genfund.grow(self.macro,repay)

        if self.year <= self.history.columns[-1]:
            self.summary.loc['generation fund',self.year] = self.history.loc['gfund_balance_end',self.year]
            self.summary.loc['fund contribution',self.year] = self.history.loc['gfund_revenue',self.year] + self.history.loc['gfund_returns',self.year]
        else :
            self.summary.loc['generation fund',self.year] = self.genfund.balance
            self.summary.loc['fund contribution',self.year] = self.genfund.contrib
        net_surplus = surplus - self.summary.loc['fund contribution',self.year]
        self.summary.loc['net surplus',self.year] = net_surplus
        if self.year <= self.history.columns[-1]:
            self.summary.loc['debt',self.year] = self.history.loc['debt_balance_end',self.year]
            self.summary.loc['gross debt',self.year] = self.history.loc['gross_debt',self.year]
            self.summary.loc['gdp',self.year] = self.history.loc['gdp',self.year]
            self.summary.loc['debt-to-gdp',self.year] = self.summary.loc['gross debt',self.year]/self.summary.loc['gdp',self.year]
            self.summary.loc['gdp growth',self.year] = self.history.loc['gdp_growth',self.year] + self.macro.infl
            self.summary.loc['pop growth',self.year] = np.nan
            self.summary.loc['emp growth',self.year] = np.nan
            self.summary.loc['reserve',self.year] = self.history.loc['reserve_balance_end',self.year]
        else:
            repay += self.reserve.grow(net_surplus,self.summary.loc['total spending',self.year])
            self.summary.loc['reserve',self.year] = self.reserve.balance
            if repay<0.0:
                self.debt.borrowing(-repay)
            else :
                self.debt.repaying(repay)
            self.debt.grow(self.macro,self.pop,self.eco)
            self.summary.loc['debt',self.year] = self.debt.balance
            self.summary.loc['gross debt',self.year] = self.debt.balance + self.debt.debt_pension.value  - self.genfund.balance - self.debt.gross_debt_reduct.value
            self.summary.loc['gdp',self.year] = self.macro.Y
            self.summary.loc['debt-to-gdp',self.year] = self.summary.loc['gross debt',self.year]/self.macro.Y
            self.summary.loc['gdp growth',self.year] = self.macro.gr_Y + self.macro.infl
            self.summary.loc['pop growth',self.year] = self.macro.gr_N
            self.summary.loc['emp growth',self.year] = self.macro.gr_L
        self.year +=1
        return
    def collect_revenue(self):
        """Fonction qui comptabilise les comptes de revenues

        Pour les années avec historique, la valeur est celle réalisée alors que pour les autres années, la valeur est celle projetée.
        """
        if self.year > self.history.columns[-1]:
            self.summary.loc['personal',self.year] = (self.revenue.personal_taxes.value +
                                                      self.revenue.personal_credits.value)
            self.summary.loc['corporate',self.year] = (self.revenue.corporate_taxes.value +\
                self.revenue.corporate_credits.value)
            self.summary.loc['consumption',self.year] = self.revenue.consumption.value
            self.summary.loc['other taxes',self.year] = (self.revenue.sum() -\
                self.summary.loc[['personal','corporate','consumption'],self.year].sum())
            self.summary.loc['autonomous',self.year] = self.revenue.sum()
            self.summary.loc['federal transfers',self.year] = self.transfers.sum()
            self.summary.loc['total revenue',self.year] = self.summary.loc['autonomous',self.year] +\
                self.summary.loc['federal transfers',self.year]
        else :
            self.summary.loc['personal',self.year] = (self.history.loc['personal_taxes',self.year] +
                                                      self.history.loc['personal_credits',self.year])

            self.summary.loc['corporate',self.year] = (self.history.loc['corporate_taxes',self.year] +
                                                       self.history.loc['corporate_credits',self.year])

            self.summary.loc['consumption',self.year] = self.history.loc['consumption',self.year]

            self.summary.loc['other taxes',self.year] = (self.history.loc['other_taxes',self.year] +
                                                         self.history.loc['permits',self.year] +
                                                         self.history.loc['fss',self.year] +
                                                         self.history.loc['gov_enterprises',self.year] +
                                                         self.history.loc['property_taxes',self.year])

            self.summary.loc['autonomous',self.year] = (self.summary.loc['personal',self.year] +
                                                        self.summary.loc['corporate',self.year] +
                                                        self.summary.loc['consumption',self.year] +
                                                        self.summary.loc['other taxes',self.year])

            self.summary.loc['federal transfers',self.year] = (self.history.loc['equalization',self.year] +
                                                               self.history.loc['health_transfer',self.year] +
                                                               self.history.loc['other_transfers',self.year])

            self.summary.loc['total revenue',self.year] = (self.summary.loc['autonomous',self.year] +
                                                          self.summary.loc['federal transfers',self.year])
        return
    def collect_spending(self):
        """Fonction qui comptabilise les comptes de dépenses

        Pour les années avec historique, la valeur est celle réalisée alors que pour les autres années, la valeur est celle projetée.
        """
        if self.year > self.history.columns[-1]:
            self.summary.loc['mission health',self.year] = self.missions.health.value
            self.summary.loc['mission education',self.year] = self.missions.education.value
            self.summary.loc['mission family',self.year] = self.missions.family.value
            self.summary.loc['other missions',self.year] = self.missions.sum() - self.missions.health.value -\
                self.missions.education.value - self.missions.family.value
            self.summary.loc['mission spending',self.year] = self.missions.sum()
            self.summary.loc['debt service',self.year] = self.debt.service()
            self.summary.loc['total spending',self.year] = self.missions.sum() + self.summary.loc['debt service',self.year]
        else :
            self.summary.loc['mission health',self.year] = self.history.loc['health',self.year]
            self.summary.loc['mission education',self.year] = self.history.loc['education',self.year]
            self.summary.loc['mission family',self.year] = self.history.loc['family',self.year]
            self.summary.loc['other missions',self.year] = (self.history.loc['economy',self.year] +\
                self.history.loc['justice',self.year])
            self.summary.loc['mission spending',self.year] = (self.summary.loc['mission health',self.year] +\
                self.summary.loc['mission education',self.year] + self.summary.loc['mission family',self.year] + self.summary.loc['other missions',self.year])
            self.summary.loc['debt service',self.year] = self.history.loc['debt_service',self.year]
            self.summary.loc['total spending',self.year] = (self.summary.loc['mission spending',self.year] +\
                 self.summary.loc['debt service',self.year])
        return
    def simulate(self,nyears=None):
        """Fonction qui exécute la projection

        Keyword Arguments:
            nyears {int} -- nombre d'année à exécuter (défaut: toutes les années jusqu'à stop_yr)
        """
        if nyears == None:
            nyears = self.stop_yr - self.start_report + 1
        for t in range(self.year,min(self.year+nyears,self.stop_yr)):
            self.next()
        return
    def reset(self):
        """Fonction qui reset le simulateur
        """
        self.reserve.reset()
        self.revenue.reset()
        self.transfers.reset()
        self.missions.reset()
        self.debt.reset()
        self.genfund.reset()
        self.macro.reset(self.pop[self.start_yr],self.eco_first)
        self.summary = pd.DataFrame(index=self.names,columns=[t for t in range(self.start_yr,self.stop_yr)])
        self.year = self.start_yr
    def replication(self,rep=1,param=None):
        """Fonction qui exécute des réplicatoins de simulation
        Keyword Arguments:
            rep {int} -- nombre de réplicatoin (défaut: 1)
        """
        def decorator_replication(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.all_summary = []
                for i in range(rep):
                    if param != None :
                        for key in param:
                            draw = np.random.random_sample()
                            index = np.searchsorted(param[key][1],draw)
                            key(self,param[key][0][index])
                    func(self,*args, **kwargs)
                    self.all_summary.append(self.summary)
                    self.reset()
            return wrapper
        return decorator_replication
