import os
import pandas as pd
from simfin.tools import account 
module_dir = os.path.dirname(os.path.dirname(__file__))

class education(account):
    def __init__(self,value,igdp=False,ipop=True,iprice=True):
        self.value = value 
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice 
        self.ipop = ipop 
        self.pcap_start = pd.read_pickle(module_dir+'/params/educ_costs.pkl')
        self.pcap = self.pcap_start['pcap'].astype('float')
        if self.iprice:
            self.price_college = 0.005 
            self.price_hs = 0.005
        else :
            self.price_college = 0.0
            self.price_hs = 0.0
        self.align = 1.0
        return    
    def set_align(self,pop):
        work = pop[pop.index.get_level_values(2)]
        work = work.groupby('age').sum()
        value = work.multiply(self.pcap,fill_value=0.0).sum()*1e-6
        self.align = self.value/value
        print('alignment factor for education : ', self.align)
        return       
    def grow(self,macro,pop,eco):
        rate = 1.0 + macro.infl
        if self.iprice:
            self.grow_pcap()
        if self.igdp: 
            rate += macro.gr_Y 
        work = pop[pop.index.get_level_values(2)]
        work = work.groupby('age').sum()
        self.value = work.multiply(self.pcap,fill_value=0.0).sum()*1e-6
        self.value *= self.align
        self.value *= rate
        return 
    def grow_pcap(self):
        self.pcap[self.pcap.index<=17] *= (1.0+self.price_hs) 
        self.pcap[self.pcap.index>=18] *= (1.0+self.price_college)
        return        
    def reset(self):
        self.value = self.start_value
        self.pcap = self.pcap_start['pcap'].astype('float')
        return 
