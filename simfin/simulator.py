import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
module_dir = os.path.dirname(os.path.dirname(__file__))
import functools
import time
from simfin import profiler, macro, revenue, missions, federal, debt, genfund, balance, reserve

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
    def __init__(self,start_yr,stop_yr,stochastic=True):
        if start_yr>2022 :
            raise ValueError('La simulation doit commencer en 2021 ou avant...')
        else:
            self.start_yr = 2022
        self.stop_yr = stop_yr
        self.year = self.start_yr
        self.maxyrs = self.stop_yr - self.start_yr + 1
        self.set_pop()
        self.set_profiles()
        self.set_macro(stochastic)
        self.init_revenue()
        self.init_missions()
        self.init_federal()
        self.init_debt()
        self.init_genfund()
        self.init_balance()
        self.init_reserve()
        return
    def set_pop(self,pop=None,file_pop='/simfin/params/simpop.csv'):
        if pop!=None:
            self.pop = pop
        else :
            self.pop = pd.read_csv(module_dir+file_pop,sep=';')
        self.pop = self.pop.set_index(['age', 'educ','insch','male','nkids','married'])
        self.pop = self.pop[[str(x) for x in range(self.start_yr-1,
                                                   self.stop_yr+1)]]
        self.pop.columns = [int(x) for x in self.pop.columns]
        return
    def set_profiles(self):
        self.profiles = profiler(self.pop.index)
        return
    def set_macro(self,stochastic):
        self.macro = macro(self.start_yr,self.stop_yr,stochastic)
        self.profiles.eco = self.macro.set_align(self.pop[self.start_yr-1],
                                       self.profiles.eco)
        return
    def init_revenue(self):
        """Fonction d'initialisation des revenus autonome

        Fonction qui crée les comptes de revenus et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.

        """
        self.hist_revenue = pd.read_excel(
            module_dir+'/simfin/revenue/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_revenue.set_index('account',inplace=True)
        current_revenue_accounts = self.hist_revenue[['e_trend','e_cycle',
                                              self.start_yr-1]]
        current_revenue_accounts.columns = ['e_trend','e_cycle','start_value']
        self.revenue = revenue.collector(current_revenue_accounts,revenue,self.start_yr)
        if self.start_yr in self.hist_revenue:
            self.revenue.set_future_value(self.hist_revenue,self.revenue,self.start_yr)
        self.profiles.tax = self.revenue.consumption.set_align(self.pop[
                                              self.start_yr-1],
                                              self.profiles.eco,self.profiles.tax)
        self.profiles.tax = self.revenue.personal_taxes.set_align(self.pop[
                                              self.start_yr-1],
                                              self.profiles.eco,self.profiles.tax)
        self.profiles.tax = self.revenue.personal_credits_family.set_align(
                                              self.pop[self.start_yr-1],self.profiles.eco,self.profiles.tax)
        self.revenue.init_report(self.start_yr)
        return
    def init_missions(self):
        """Fonction d'initialisation des dépenses de missions

        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.

        """
        self.hist_missions = pd.read_excel(
            module_dir+'/simfin/missions/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_missions.set_index('account',inplace=True)
        current_missions_accounts = self.hist_missions[['e_trend','e_cycle',self.start_yr-1]]
        current_missions_accounts.columns = ['e_trend','e_cycle','start_value']
        self.missions = missions.collector(current_missions_accounts,missions,start_yr=self.start_yr)
        if self.start_yr in self.hist_missions:
            self.missions.set_future_value(self.hist_missions,self.missions,self.start_yr)
        self.missions.health.set_align(self.pop[self.start_yr-1])
        self.missions.education.set_align(self.pop[self.start_yr])
        self.missions.family_credit.set_align(self.pop[self.start_yr],self.profiles.eco,self.profiles.tax)
        self.profiles.tax = self.missions.family_credit.set_align(self.pop[self.start_yr-1],self.profiles.eco,self.profiles.tax)
        self.missions.family_kg.set_sub_account(self.macro,self.pop[self.start_yr])
        self.missions.init_report(self.start_yr)
        return
    def init_federal(self):
        """Fonction d'initialisation des dépenses de missions

        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.

        """
        self.hist_federal = pd.read_excel(
            module_dir+'/simfin/federal/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_federal.set_index('account',inplace=True)
        current_federal_accounts = self.hist_federal[['e_trend','e_cycle',self.start_yr-1]]
        current_federal_accounts.columns = ['e_trend','e_cycle','start_value']
        self.federal = federal.collector(current_federal_accounts,federal, start_yr=self.start_yr)
        if self.start_yr in self.hist_federal:
            self.federal.set_future_value(self.hist_federal,self.federal,self.start_yr)
        self.federal.init_report(self.start_yr)
        return

    def init_genfund(self):
        """Fonction d'initialisation des dépenses de missions
        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        self.hist_genfund = pd.read_excel(
            module_dir+'/simfin/genfund/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_genfund.set_index('account',inplace=True)
        current_genfund_accounts = self.hist_genfund[['e_trend','e_cycle',self.start_yr-1]]
        current_genfund_accounts.columns = ['e_trend','e_cycle','start_value']
        self.genfund = genfund.collector(current_genfund_accounts,genfund,self.start_yr)

        if self.start_yr in self.hist_genfund:
            self.genfund.set_future_value(self.hist_genfund.iloc[:-2,:],self.genfund,self.start_yr)
        self.genfund.placements.capital_gain=0
        self.genfund.init_report(self.start_yr)
        return
    def init_debt(self):
        """Fonction d'initialisation de la dette
        Fonction qui crée les comptes de la dette avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        self.hist_debt = pd.read_excel(
            module_dir+'/simfin/debt/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_debt.set_index('account',inplace=True)

        current_debt_accounts = self.hist_debt[['e_trend','e_cycle',self.start_yr-1]]
        current_debt_accounts.columns = ['e_trend','e_cycle','start_value']
        self.debt = debt.collector(current_debt_accounts,debt,self.start_yr)

        if self.start_yr in self.hist_debt:
            self.debt.set_future_value(self.hist_debt,self.debt,self.start_yr)

        self.debt.init_report(self.start_yr)
        return
    def init_balance(self):
        """Fonction d'initialisation du surplus annuel et du solde budgétaire avant réserve de stabilisation
        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        self.hist_balance = pd.read_excel(
            module_dir+'/simfin/balance/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_balance.set_index('account',inplace=True)
        current_balance_accounts = self.hist_balance[['e_trend','e_cycle',self.start_yr-1]]
        current_balance_accounts.columns = ['e_trend','e_cycle','start_value']
        self.balance = balance.collector(current_balance_accounts,balance,self.start_yr)

        if self.start_yr in self.hist_balance:
            self.balance.set_future_value(self.hist_balance,self.balance,self.start_yr)

        self.balance.init_report(self.start_yr)
        return
    def init_reserve(self):
        """Fonction d'initialisation de la réserve de stabilisation et du solde budgétaire après réserve de stabilisation 
        Fonction qui crée les comptes de missions et les initialise avec valeur de départ provenant de l'historique des comptes publics pour l'année de départ.
        """
        self.hist_reserve = pd.read_excel(
            module_dir+'/simfin/reserve/historical_accounts.xlsx',
                                    sheet_name='input')
        self.hist_reserve.set_index('account',inplace=True)
        current_reserve_accounts = self.hist_reserve[['e_trend','e_cycle',self.start_yr-1]]
        current_reserve_accounts.columns = ['e_trend','e_cycle','start_value']
        self.reserve = reserve.collector(current_reserve_accounts,reserve,self.start_yr)

        if self.start_yr in self.hist_reserve:
            self.reserve.set_future_value(self.hist_reserve,self.reserve,self.start_yr)

        self.reserve.init_report(self.start_yr)
        return
    def next(self):
        self.profiles.update()
        if self.year >= self.start_yr:
            self.macro.grow(self.year,self.pop[self.year],self.profiles.eco)
            self.revenue.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)
            self.missions.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)
            self.federal.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)
            self.genfund.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)

            self.debt.interests(self.year)
            self.balance.grow(self.revenue.sum(),self.missions.sum(),self.federal.sum(), self.genfund.sum(),self.debt.interest_value)
            self.reserve.grow(getattr(self.balance.budget_balance,'value'),self.reserve.reserve_balance.value)

            #self.placements.grow()
            #self.fixed_assets.grow()
            #self.pension.grow()

            if self.year > self.start_yr:   
                delta_genfund = self.genfund.value-self.genfund.report.loc['Valeur comptable',self.year-1]
                delta_direct_debt = self.genfund.value-self.genfund.report.loc['Valeur comptable',self.year-1]
            else:
                delta_genfund = self.genfund.value - 12210
                delta_direct_debt = self.hist_debt.loc['direct_debt',self.year-1]

            self.debt.grow(getattr(self.balance.budget_balance,'value'),0,0,0,0,delta_genfund,0)
            self.debt.structure_update(self.macro,delta_direct_debt, self.year)
        return
    def simulate(self):
        while (self.year < self.stop_yr):
            self.next()
            self.revenue.report_back(self.year)
            self.missions.report_back(self.year)
            self.federal.report_back(self.year)
            self.debt.report_back(self.year)
            self.genfund.report_back(self.year)
            self.balance.report_back(self.year)
            self.reserve.report_back(self.year)
            self.year += 1
        return
    def reset(self):
        self.year = self.start_yr
        return
