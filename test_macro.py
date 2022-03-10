from simfin import macro
import numpy as np
from matplotlib import pyplot as plt


x = macro(2021,2050)
x.set_shocks()
x.grow(2021)
