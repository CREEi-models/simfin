import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
module_dir = os.path.dirname(os.path.dirname(__file__))
import functools
import time
from simfin import profiler, macro, revenue, missions

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
        if start_yr>2021 :
            raise ValueError('La simulation doit commencer en 2021 ou avant...')
        else:
            self.start_yr = 2021
        self.stop_yr = stop_yr
        self.year = self.start_yr
        self.maxyrs = self.stop_yr - self.start_yr + 1
        self.set_pop()
        self.set_profiles()
        self.set_macro(stochastic)
        self.init_revenue()
        self.init_missions()
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
        self.revenue = revenue.collector(current_revenue_accounts,revenue)
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
        current_missions_accounts = self.hist_missions[['e_trend','e_cycle',
                                                         self.start_yr-1]]
        current_missions_accounts.columns = ['e_trend','e_cycle','start_value']
        self.missions = missions.collector(current_missions_accounts,missions)
        self.missions.init_report(self.start_yr)
        return
    def next(self):
        self.profiles.update()
        if self.year >= self.start_yr:
            self.macro.grow(self.year,self.pop[self.year],self.profiles.eco)
            self.revenue.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)
            self.missions.grow(self.macro,self.pop[self.year],self.profiles.eco,
                              self.profiles.tax)
        return
    def simulate(self):
        while (self.year < self.stop_yr):
            self.next()
            self.revenue.report_back(self.year)
            self.missions.report_back(self.year)
            self.year += 1
        return
    def reset(self):
        self.year = self.start_yr
        return
