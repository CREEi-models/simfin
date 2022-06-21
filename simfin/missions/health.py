import os
import pandas as pd
from simfin.tools import account
module_dir = os.path.dirname(os.path.dirname(__file__))

class health(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission Santé et services sociaux.
    '''
    def __init__(self,value,e_trend=0.0,e_cycle=0.0,start_yr=2022):
        self.year=start_yr
        self.future_value = pd.DataFrame()
        self.value = value
        self.start_value = value
        self.pcap_start = pd.read_csv(module_dir+'/params/health_cihi_pcap.csv', sep = ';')
        self.pcap_start = self.pcap_start.set_index(['age', 'male'])
        self.pcap = self.pcap_start.copy()
        self.tcam = pd.read_csv(module_dir+'/params/health_cihi_growth.csv', sep = ';')
        self.tcam = self.tcam.set_index(['age', 'male'])
        self.categories = ['Drugs','Hospitals','Other Institutions','Other Professionals','Physicians']
        self.align = 1.0
        return
    def set_align(self,pop):
        total = pop.groupby(['age','male']).sum()
        value = total.multiply(self.pcap['Total'],fill_value=0.0).sum()*1e-6
        self.align = self.value/value
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.inflrate
        tau = (min(macro.yr,macro.start_yr+10) - macro.start_yr)/10.0
        self.grow_pcap(tau)
        total = pop.groupby(['age','male']).sum()
        self.value = total.multiply(self.pcap['Total'],fill_value=0.0).sum()*1e-6
        self.value *= self.align
        if self.year in self.future_value:
            self.value = self.future_value[self.year]
        else : self.value *= rate
        self.align *= rate
        self.year+=1
        return
    def grow_pcap(self,tau):
        rates = self.tcam[self.categories]
        total = self.tcam['Total']
        self.pcap = self.pcap.copy()
        for c in self.categories:
            rates.loc[:,c] = (1.0-tau)*rates.loc[:,c] + tau*total
            self.pcap[c] = self.pcap[c] * (1.0 + rates[c])
        self.pcap['Total'] = self.pcap[self.categories].sum(axis=1)
        return
    def reset(self):
        self.value = self.start_value
        self.pcap = self.pcap_start.copy()
        return
