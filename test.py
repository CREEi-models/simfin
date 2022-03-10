from simfin import simulator, replicator
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

x = simulator(2021, 2050,stochastic=False)

# def wmean(x,var,yr):
#     xx = x.loc[~x[var].isna(),:]
#     names = {var: (xx[var] * xx[yr]).sum()/xx[yr].sum()}
#     return pd.Series(names, index=[var])
#
#
# stats = x.pop.merge(x.profiles.tax,left_index=True,right_index=True,how='left')
# stats.loc[stats.cons_tax_rate.isna(),'cons_tax_rate'] = 0.0
# stats = stats.merge(x.profiles.eco,left_index=True,right_index=True,how='left')
# stats.loc[stats.earn_c.isna(),'earn_c'] = 0.0
# stats.loc[stats.emp.isna(),'emp'] = 0.0
# stats.loc[stats.non_work_taxinc.isna(),'non_work_taxinc'] = 0.0
# stats['inc_rev'] = stats['personal_tax_rate']*(stats['earn_c']*stats[
#     'emp']+stats['non_work_taxinc'])*1e6
# age = stats.groupby(['age','educ']).apply(wmean,var='inc_rev',
#                                           yr=2020).unstack()
# plt.plot(age.index,age)
# plt.show()

mc = replicator(nreps=2, ncpus=2)
mc.set_model(x)
mc.replicate()


plt.figure()
for m in mc.models:
	gr = m.macro.aggr['gr_Y']
	plt.plot(m.macro.aggr.index, gr)
plt.title('growth')
plt.show()

plt.figure()
for m in mc.models:
	gr = m.macro.aggr['gr_H']
	plt.plot(m.macro.aggr.index, gr)
plt.title('hours')
plt.show()

plt.figure()
for m in mc.models:
	gr = m.macro.aggr['gr_YperH']
	plt.plot(m.macro.aggr.index, gr)
plt.title('output per hours')
plt.show()

plt.figure()
for m in mc.models:
	gr = m.macro.aggr['infl']
	plt.plot(m.macro.aggr.index, gr)
plt.title('inflation rate')
plt.show()

plt.figure()
for m in mc.models:
	gr = m.macro.aggr['E']
	plt.plot(m.macro.aggr.index, gr)
plt.title('employment')
plt.show()

plt.figure()
for m in mc.models:
	gr = m.macro.aggr['Y']
	gr2 = m.macro.aggr['Yp']
	plt.plot(m.macro.aggr.index, gr,label='output')
	plt.plot(m.macro.aggr.index, gr2,label='potential')
plt.title('output')
plt.legend()
plt.show()

plt.figure()
for m in mc.models:
	r  = m.revenue.report.loc['consumption',:]
	gr = r/r.shift(1)-1
	plt.plot(r.index, gr)
plt.title('consumption')
plt.show()


plt.figure()
for m in mc.models:
	r  = m.revenue.report.loc['personal_taxes',:]
	gr = r/r.shift(1)-1
	plt.plot(r.index, gr)
plt.title('personal taxes')
plt.show()