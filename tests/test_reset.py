import numpy as np
from matplotlib import pyplot as plt
from importlib import reload 
import sys 
#sys.path.append('/users/loulou/cedia/simfin/Model')
import warnings
import simfin
warnings.filterwarnings('ignore')
x = simfin.simulator(2019,2021)
def change_inflation(inf):
    x.macro.infl = inf
    print(type(inf))
infl = list(np.linspace(0,3,10))
@x.replication(rep=10,param={change_inflation:infl})
def my_simulation():
    x.simulate()
my_simulation()


