import pandas as pd
import numpy as np
from simfin import revenue, macro, federal, missions, debt, genfund, reserve, pension, placements, fixed_assets
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
    def __init__(self,start_report,stop_yr,melt=None):
        if start_report>2020 :
            raise ValueError('Les statistiques doivent commencer entre 2006 et 2019')
        else:
            self.start_report = start_report
        self.start_yr = 2020
        self.stop_yr = stop_yr
        self.year = self.start_report
        self.maxyrs = self.stop_yr - self.start_report + 1
        self.macro = macro(self.start_yr)
        self.load_accounts()
        self.load_params()
        if melt!=None:
            self.melt(melt)
        self.align_targets()
        self.init_revenue()
        self.init_transfers()
        self.init_missions() #need to be after self.init_revenue()
        self.init_gfund()
        self.init_reserve()
        self.init_debt()
        self.init_pension_debt()
        self.init_placements()
        self.init_fixed_assets()
        return
    def align_targets(self):
        self.macro.set_align_emp(self.pop[self.start_yr],self.eco)
        self.macro.set_align_cons(self.pop[self.start_yr],self.eco)
        return
    def load_accounts(self):
        """
        Fonction permettant de charger l'historique des comptes publics.

        L'historique des comptes publics a été comptabilisé pour la période 2006-2019. Cette fonction charge les valeurs des comptes publics et prépare le rapport sommaire (summary report) pour les résultats.

        NB: debt = dette avant gains de change - emprunts réalisés par anticipation

        """
        self.history = pd.read_excel(module_dir+'/simfin/params/historical_accounts.xlsx',sheet_name='Inputs')
        self.history = self.history.set_index('account')
        self.names = ['personal','corporate','consumption','miscellaneous income','permits','fss','government entreprises',
            'property taxes','autonomous','federal transfers',
            'total revenue','mission health','mission education','mission family','other missions','mission spending',
            'debt service','debt service without pension interests','total spending','annual surplus','generation fund','fund contribution','fund payment','budget balance',
            'reserve','debt','gross debt','gdp','change gross debt no deficit','gross-debt-to-gdp','gdp growth','pop growth','emp growth','pension debt',
            'pension interests','stock placements/others','flow placements','flow others','stock fixed assets','flow fixed assets']
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
        #print('non_work/earnings :', non_work_earnings/earnings )
        return
    def weighted_average(self,df,data_col,weight_col,by_col):
        df['_data_times_weight'] = df[data_col]*df[weight_col]
        df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
        g = df.groupby(by_col)
        result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
        del df['_data_times_weight'], df['_weight_where_notnull']
        result.loc[result.isna()] = 0.0
        return result
    def melt(self,var):
        stratas = self.eco.index.names
        stratas = [s for s in stratas if s!=var]
        work = self.eco.merge(self.pop[self.year],left_index=True,right_index=True)
        result = self.weighted_average(work,'emp',self.start_yr,stratas).to_frame()
        result.columns = ['emp']
        for c in ['earn_c','cons','hours_c','cons_taxes','taxinc','personal_taxes','credit_famille']:
            result[c] = self.weighted_average(work,c,self.start_yr,stratas)
        self.eco = result
        stratas = [s for s in self.pop.index.names if s!=var]
        self.pop = self.pop.groupby(stratas).sum()
        return
    def init_revenue(self):
        """Fonction initialisation des revenues

        Fonction qui crée les comptes de revenus et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.

        """
        revenue_accounts = self.history.loc[:'miscellaneous_income',self.start_yr]
        self.others_dict_account = {'gfund_inc_init': self.history.loc['gfund_returns',self.start_yr]}
        self.revenue = revenue.collector(revenue_accounts,revenue,self.others_dict_account)
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
        # names = ['debt_borrow','debt_depr_fund','debt_ppp','gross_debt_reduct']

        # TO BE CHANGED
        balance_start = self.history.loc['debt_balance_end',self.start_yr] # start with end as grow only launched at start_yr+1
        self.debt = debt.collector(balance_start)
        return
    def init_gfund(self):
        """Fonction initialisation du fonds des générations.

        Fonction qui crée les comptes du fonds des générations et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        balance_start = self.history.loc['gfund_balance_end',self.start_yr]
        self.genfund = genfund.collector(balance_start)
        return

    def init_reserve(self):
        """Fonction initialisation de la réserve de stabilisation.

        Fonction qui crée les comptes de la réserve de stabilisation et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        balance_end = self.history.loc['reserve_balance_end',self.start_yr]
        self.reserve = reserve.collector(balance_end)
        return

    def init_pension_debt(self):
        """Fonction initialisation la dette des pensions.

        Fonction qui crée les comptes de la dette des pensions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        self.pension_data = pd.read_excel(module_dir+'/simfin/params/historical_accounts.xlsx',sheet_name='pension_balance')
        self.pension_data = self.pension_data.set_index('vars')

        init_liabilities = self.pension_data.loc['pension - liabilities end',self.start_yr] \
            + self.pension_data.loc['pension - liabilities future social advantages',self.start_yr]
        init_assets      = self.pension_data.loc['pension - assets',self.start_yr]  \
            + self.pension_data.loc['pension - assets future social advantages',self.start_yr]
        init_actuarial_changes = self.pension_data.loc['pension - actuarial changes not amortized',self.start_yr]

        init_new_liabilities  = self.pension_data.loc['pension - new liabilities',self.start_yr]
        init_paid_liabilities = self.pension_data.loc['pension - paid liabilities',self.start_yr]

        self.pension_debt     = pension.collector(init_liabilities,init_assets,init_actuarial_changes,
                                                  init_new_liabilities,init_paid_liabilities)
        return

    def init_placements(self):

        """Fonction initialisation la dette des pensions.

        Fonction qui crée les comptes de la dette des pensions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        init_balance = self.history.loc['placements and other assets/debts',self.start_yr]
        self.placements_and_others = placements.collector(init_balance)
        return

    def init_fixed_assets(self):

        """Fonction initialisation la dette des pensions.

        Fonction qui crée les comptes de la dette des pensions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        init_balance = self.history.loc['fixed assets',self.start_yr]
        self.fixed_assets = fixed_assets.collector(init_balance)
        return

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
            self.others_dict_account['gfund_inc'] = self.genfund.returns()
            self.revenue.grow(self.macro,self.pop[self.year],self.eco,self.others_dict_account)
            self.transfers.grow(self.macro,self.pop[self.year],self.eco)
            self.missions.grow(self.macro,self.pop[self.year],self.eco)
            self.pension_debt.compute_interests()

        # revenue
        self.collect_revenue()
        # spending
        self.collect_spending()

        # growth assets
        if self.year>self.start_yr:
            self.pension_debt.grow(self.macro,self.year)
            self.placements_and_others.grow(self.year,self.macro.Y)
            self.fixed_assets.grow(self.year,self.macro.Y)

        # FDG
        repay = 0.0
        if self.year <= self.history.columns[-1]:
            repay += self.history.loc['debt_repay',self.year]
        repay_exo = 0
        if self.year <= self.history.columns[-1]:
            self.summary.loc['fund payment',self.year] = repay
        else:
            self.genfund.grow(self.macro,repay_exo)
            self.summary.loc['fund payment',self.year] = self.genfund.repay

        # annual surplus
        annual_surplus = self.summary.loc['total revenue',self.year] - self.summary.loc['total spending',self.year]
        self.summary.loc['annual surplus',self.year] = annual_surplus

        # FDG
        if self.year <= self.history.columns[-1]:
            self.summary.loc['generation fund',self.year] = self.history.loc['gfund_balance_end',self.year]
            self.summary.loc['fund contribution',self.year] = self.history.loc['gfund_revenue',self.year] + self.history.loc['gfund_returns',self.year]
        else :
            self.summary.loc['generation fund',self.year] = self.genfund.balance
            self.summary.loc['fund contribution',self.year] = self.genfund.contrib

        budget_balance = annual_surplus - self.summary.loc['fund contribution',self.year]
        self.summary.loc['budget balance',self.year] = budget_balance

        # DEBT
        if self.year <= self.history.columns[-1]:
            self.summary.loc['debt',self.year] = self.history.loc['debt_balance_end',self.year]
            self.summary.loc['gross debt',self.year] = self.history.loc['gross_debt',self.year]
            self.summary.loc['gdp',self.year] = self.history.loc['gdp',self.year]
            self.summary.loc['gross-debt-to-gdp',self.year] = self.summary.loc['gross debt',self.year]/self.summary.loc['gdp',self.year]
            self.summary.loc['gdp growth',self.year] = self.history.loc['gdp_growth',self.year] + self.macro.infl
            self.summary.loc['pop growth',self.year] = np.nan
            self.summary.loc['emp growth',self.year] = np.nan
            self.summary.loc['reserve',self.year] = self.history.loc['reserve_balance_end',self.year]
            self.summary.loc['pension debt',self.year] = self.history.loc['pension_balance',self.year]
            self.summary.loc['stock placements/others',self.year] = self.history.loc['placements and other assets/debts',self.year]
            self.summary.loc['stock fixed assets',self.year] = self.history.loc['fixed assets',self.year]
            self.summary.loc['flow placements',self.year] = self.history.loc['flow placements and other assets/debts',self.year]
            self.summary.loc['flow fixed assets',self.year] = self.history.loc['flow fixed assets',self.year]
        else:
            # GROWTH DEBT
            # variation of the different assets + surplus
            self.debt.grow(self.macro,self.placements_and_others.net_placements,self.placements_and_others.net_other_factors,
            self.fixed_assets.investment_fixed_assets,budget_balance,self.pension_debt.balance_change,self.genfund.repay)

            self.summary.loc['debt',self.year] = self.debt.balance
            self.summary.loc['gross debt',self.year] = self.debt.balance + self.pension_debt.balance - self.genfund.balance

            #+ self.debt.debt_pension.value  - self.genfund.balance - self.debt.gross_debt_reduct.value
            self.summary.loc['gdp',self.year] = self.macro.Y
            self.summary.loc['gross-debt-to-gdp',self.year] = self.summary.loc['gross debt',self.year]/self.macro.Y
            self.summary.loc['gdp growth',self.year] = self.macro.gr_Y + self.macro.infl
            self.summary.loc['pop growth',self.year] = self.macro.gr_N
            self.summary.loc['emp growth',self.year] = self.macro.gr_L
            self.summary.loc['pension debt',self.year] = self.pension_debt.balance
            self.summary.loc['stock placements/others',self.year] = self.placements_and_others.balance
            self.summary.loc['flow placements',self.year] = self.placements_and_others.net_placements
            self.summary.loc['flow others',self.year] = self.placements_and_others.net_other_factors
            self.summary.loc['stock fixed assets',self.year] = self.fixed_assets.balance
            self.summary.loc['flow fixed assets',self.year] = self.fixed_assets.investment_fixed_assets
            self.summary.loc['change gross debt no deficit',self.year] = self.summary.loc['gross debt',self.year]-\
                self.summary.loc['gross debt',self.year-1] + self.summary.loc['budget balance',self.year]


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
            self.summary.loc['miscellaneous income',self.year] = self.revenue.miscellaneous_income.value
            self.summary.loc['permits',self.year] = self.revenue.permits.value
            self.summary.loc['fss',self.year] = self.revenue.fss.value
            self.summary.loc['government entreprises',self.year] = self.revenue.gov_enterprises.value
            self.summary.loc['property taxes',self.year] = self.revenue.property_taxes.value
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

            self.summary.loc['miscellaneous income',self.year] = self.history.loc['miscellaneous_income',self.year]

            self.summary.loc['permits',self.year] = self.history.loc['permits',self.year]
            self.summary.loc['fss',self.year] = self.history.loc['fss',self.year]
            self.summary.loc['government entreprises',self.year] = self.history.loc['gov_enterprises',self.year]
            self.summary.loc['property taxes',self.year] = self.history.loc['property_taxes',self.year]

                        # self.history.loc['permits',self.year] +
                        #                                  self.history.loc['fss',self.year] +
                        #                                  self.history.loc['gov_enterprises',self.year] +
                        #                                  self.history.loc['property_taxes',self.year])

            self.summary.loc['autonomous',self.year] = (self.summary.loc['personal',self.year] +
                                                        self.summary.loc['corporate',self.year] +
                                                        self.summary.loc['consumption',self.year] +
                                                        self.summary.loc['miscellaneous income',self.year]+
                                                        self.history.loc['permits',self.year] +
                                                        self.history.loc['fss',self.year] +
                                                        self.history.loc['gov_enterprises',self.year] +
                                                        self.history.loc['property_taxes',self.year])

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
            self.summary.loc['debt service',self.year] = self.debt.debt_interest()+self.pension_debt.interests
            self.summary.loc['total spending',self.year] = self.missions.sum() + self.summary.loc['debt service',self.year]
            self.summary.loc['pension interests',self.year] = self.pension_debt.interests
            self.summary.loc['debt service without pension interests',self.year] = self.debt.debt_interest()
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
            self.summary.loc['pension interests',self.year] = self.history.loc['pension_interests',self.year]
            self.summary.loc['debt service without pension interests',self.year] = self.history.loc['debt_service',self.year] - self.history.loc['pension_interests',self.year]
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
