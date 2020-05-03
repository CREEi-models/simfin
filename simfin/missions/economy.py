from simfin.tools import account 

class economy(account):
    def __init__(self,value,igdp=True,ipop=False,iprice=False):
        self.value = value 
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice 
        self.ipop = ipop 
        return 