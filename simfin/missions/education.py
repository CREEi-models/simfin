import os
import pandas as pd
from simfin.tools import account
module_dir = os.path.dirname(os.path.dirname(__file__))

class education(account):
    '''
    Classe permettant d’intégrer les dépenses de la mission Éducation et culture.

    Parameters
    ----------
    igdp: boolean
        Switch pour intégrer ou non la croissance du PIB.
    iprice: boolean
        Switch pour intégrer ou non la croissance du niveau général des prix.
    '''
    def __init__(self,value,e_trend=0.0,e_cycle=0.0):
        self.value = value
        self.start_value = value
        self.pcap_start = pd.read_csv(module_dir+'/params/educ_costs.csv', index_col=0, sep = ';')
        self.pcap = self.pcap_start['pcap'].astype('float')
        self.align = 1.0
        self.price_hs = 2/100
        self.price_college = 0.3/100
        return
    def set_align(self,pop):
        work = pop[pop.index.get_level_values(2)]
        work = work.groupby('age').sum()
        value = work.multiply(self.pcap,fill_value=0.0).sum()*1e-6
        self.align = self.value/value
        return
    def grow(self,macro,pop,eco,others=None):
        rate = 1.0 + macro.inflrate
        self.grow_pcap()
        work = pop[pop.index.get_level_values(2)]
        work = work.groupby('age').sum()
        self.value = work.multiply(self.pcap,fill_value=0.0).sum()*1e-6
        self.align *= rate
        self.value *= self.align
        return
    def grow_pcap(self):
        self.pcap[self.pcap.index<=17] *= (1.0+self.price_hs)
        self.pcap[self.pcap.index>=18] *= (1.0+self.price_college)
        return
    def reset(self):
        self.value = self.start_value
        self.pcap = self.pcap_start['pcap'].astype('float')
        return
