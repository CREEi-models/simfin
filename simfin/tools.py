
class account:
    def __init__(self,value,igdp=False,ipop=False,iprice=False):
        self.value = value 
        self.start_value = value
        self.igdp = igdp
        self.iprice = iprice 
        self.ipop = ipop 
        return
    def grow(self,macro,pop,eco):
        rate = 1.0 + macro.infl
        if self.igdp: 
            rate += macro.gr_Y 
        if self.ipop:
            rate += macro.gr_N 
        self.value *= rate
        return 
    def reset(self):
        self.value = self.start_value
        return 

class accounts:
    def __init__(self,base,group_name):
        self.account_names = []
        for attr, value in base.items():
            self.account_names.append(attr)
            account_class = getattr(group_name,attr)
            setattr(self,attr,account_class(value))
        return 
    def sum(self):
        return sum([getattr(self, acc).value for acc in self.account_names])
    def grow(self,macro,pop,eco):
        for acc_name in self.account_names:
            acc = getattr(self, acc_name)
            acc.grow(macro,pop,eco)
            setattr(self,acc_name,acc)
        return
    def reset(self):
        for acc_name in self.account_names:
            acc = getattr(self,acc_name)
            acc.reset()
            setattr(self,acc_name,acc)
        return  
