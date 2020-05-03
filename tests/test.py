
import numpy as np
from matplotlib import pyplot as plt
from importlib import reload 
import sys 
sys.path.append('/users/loulou/cedia/simfin/Model')


from simfin import macro

from simfin import revenue 




macro = simfin.macro(2017)








pop = None
macro.set_rate_real_K(rate=0.015)
macro.set_align_emp(pop)
for t in range(2018,2060):
    macro.emp(pop)
    macro.growth()
    print(macro.L,macro.Y,macro.gr_Y)



x = simfin.simulator(2017,2060)

x.simulate()


