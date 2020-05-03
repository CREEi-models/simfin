import os
import pandas as pd
from simfin.tools import account 
module_dir = os.path.dirname(os.path.dirname(__file__))

class health(account):
    def __init__(self,value,igdp=False,ipop=True,iprice=True):
        self.value = value 
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice 
        self.ipop = ipop 
        self.pcap = pd.read_pickle(module_dir+'/params/health_cihi_pcap.pkl')
        self.tcam = pd.read_pickle(module_dir+'/params/health_cihi_growth.pkl')
        self.categories = ['Drugs','Hospitals','Other Institutions','Other Professionals','Physicians']
        self.align = 1.0
        return    
    def set_align(self,pop):
        total = pop.groupby(['age','male']).sum()
        value = total.multiply(self.pcap['Total'],fill_value=0.0).sum()*1e-6 
        self.align = self.value/value
        print('alignment factor for health : ', self.align)
        return       
    def grow(self,macro,pop,eco):
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
        return 
    def grow_pcap(self,tau):
        rates = self.tcam[self.categories]
        total = self.tcam['Total']
        if self.iprice: 
            for c in self.categories: 
                rates[c] = (1.0-tau)*rates[c] + tau*total 
                self.pcap[c] = self.pcap[c] * (1.0 + rates[c])
        self.pcap['Total'] = self.pcap[self.categories].sum(axis=1)
        return             
    def reset(self):
        self.value = self.start_value
        return 





