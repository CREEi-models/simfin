import numpy as np 
import pandas as pd
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class profiler: 
	def __init__(self,stratas):
		self.stratas = stratas
		self.load()
		return 
	def load(self,file_profiles='/simfin/params/'):
		emp = pd.read_csv(module_dir+file_profiles+'emp.csv', sep = ';')
		earn_c = pd.read_csv(module_dir+file_profiles+'earn_c.csv', sep = ';')
		cons = pd.read_csv(module_dir+file_profiles+'cons.csv', sep = ';')
		hours_c = pd.read_csv(module_dir+file_profiles+'hours_c.csv', sep = ';')
		cons_tax_rate = pd.read_csv(module_dir+file_profiles+'cons_taxes.csv', sep = ';')
		non_work_taxinc = pd.read_csv(module_dir+file_profiles+'non_work_taxinc.csv', sep = ';')
		personal_tax_rate = pd.read_csv(module_dir+file_profiles+'personal_taxes.csv', sep = ';')
		family_credits = pd.read_csv(module_dir+file_profiles+'credit_famille.csv', sep = ';')

		emp = emp.set_index(['age', 'educ','insch','male','nkids','married'])
		earn_c = earn_c.set_index(['age', 'educ','insch','male','nkids','married'])
		cons = cons.set_index(['age', 'educ','insch','male','nkids','married'])
		hours_c = hours_c.set_index(['age', 'educ','insch','male','nkids','married'])
		cons_tax_rate = cons_tax_rate.set_index(['age', 'educ','insch','male','nkids','married'])
		non_work_taxinc = non_work_taxinc.set_index(['age', 'educ','insch','male','nkids','married'])
		personal_tax_rate = personal_tax_rate.set_index(['age', 'educ','insch','male','nkids','married'])
		family_credits = family_credits.set_index(['age', 'educ','insch','male','nkids','married'])

		df = pd.DataFrame(index=self.stratas)
		df = (df.merge(emp,left_index=True,			right_index=True,how='outer').
				merge(earn_c/1e6,left_index=True, right_index=True,how='outer').
				merge(cons/1e6,left_index=True, right_index=True,how='outer').
				merge(hours_c,left_index=True, right_index=True,how='outer').
				merge(cons_tax_rate,left_index=True, right_index=True,how='outer').
				merge(non_work_taxinc/1e6,left_index=True, right_index=True,how='outer').
				merge(personal_tax_rate,left_index=True, right_index=True,how='outer').
				merge(family_credits,left_index=True, right_index=True,how='outer').
				fillna(value=0))
		df.columns = ['emp','earn_c','cons','hours_c','cons_tax_rate',
					  'non_work_taxinc','personal_tax_rate',
					  'family_credits_rate']
		self.eco = df[['emp','earn_c','cons','hours_c','non_work_taxinc']]
		self.eco['wage'] = np.where(self.eco['hours_c']>0,self.eco[
			'earn_c']/self.eco['hours_c'],0.0)
		self.tax = df[['cons_tax_rate','personal_tax_rate',
					   'family_credits_rate']]
		return
	def update(self):
		return 

	

