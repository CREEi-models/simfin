import numpy as np
from matplotlib import pyplot as plt
from importlib import reload 
import sys 
#sys.path.append('/users/loulou/cedia/simfin/Model')
import warnings
import simfin
warnings.filterwarnings('ignore')
x = simfin.simulator(2019,2021)
x.simulate()
x.reset()
x.simulate()
x.summary.loc[:,[2019]]
