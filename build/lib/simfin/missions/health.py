import os
import pandas as pd
from simfin.tools import account
module_dir = os.path.dirname(os.path.dirname(__file__))

class health(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission Santé et services sociaux.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,igdp=False,iprice=True,others=None):
        self.value = value
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice
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
        rate = 1.0 + macro.infl
        if self.iprice:
            tau = (min(macro.year,macro.start_yr+10) - macro.start_yr)/10.0
            self.grow_pcap(tau)
        if self.igdp:
            rate += macro.gr_Y
        total = pop.groupby(['age','male']).sum()
        self.value = total.multiply(self.pcap['Total'],fill_value=0.0).sum()*1e-6
        self.value *= self.align
        self.value *= rate
        self.align *= rate

        return
    def grow_pcap(self,tau):
        rates = self.tcam[self.categories]
        total = self.tcam['Total']
        if self.iprice:
            for c in self.categories:
                rates.loc[:,c] = (1.0-tau)*rates.loc[:,c] + tau*total
                self.pcap[c] = self.pcap[c] * (1.0 + rates[c])
        self.pcap['Total'] = self.pcap[self.categories].sum(axis=1)
        return
    def reset(self):
        self.value = self.start_value
        self.pcap = self.pcap_start.copy()
        return
