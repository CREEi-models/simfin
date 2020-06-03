import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from scipy.optimize import minimize

pd.options.mode.chained_assignment = None  


def prepare():
    with open('trans_schldone.csv', newline='') as f:
        reader = csv.reader(f,  delimiter=';')
        transparam = list(reader)
    transparam = dict(transparam)
    transparam.pop('var')
    for keys in transparam.keys():    
        transparam[keys] = float(transparam[keys])
    
    
    df  = pd.read_pickle('../simpop.pkl')
    df.reset_index(level=df.index.names, inplace=True)
    df = df[(df['age']>=17)&(df['age']<=35)]
    df['byear'] = 2017 - df['age']
    # create father and mother variables
    df['father'] = 0
    df.loc[(df['male']==True)&(df['nkids']>0),'father'] =1 
    df['mother'] = 0
    df.loc[(df['male']==False)&(df['nkids']>0),'mother'] =1 
    
    # dummies for age
    list_age = []
    for age in range(18,36):
        df['age'+str(age)] = np.where(df['age']==age,1,0)
        list_age.append('age'+str(age)) 
    
    # add the constant as we just want to adjust transition at 17 and keep the others at the same value
    for age_var in list_age:
        transparam[age_var] = transparam[age_var]+transparam['constant']    
    transparam['age17'] = transparam['constant']
    transparam.pop('constant') 
    
    df['age17'] = np.where(df['age']==17,1,0)
    df['predicted_val'] = 0
    
    return df, transparam

def f(x):
    
    df, transparam = prepare()
    transparam['age17'] = x*transparam['age17'] 
    
    for keys in transparam.keys():
        df['predicted_val'] += df[keys]*transparam[keys]
    
    df['predicted_val'] = 1 /(1+np.exp(-df['predicted_val']))
    # df = df.groupby(['age']).mean()
    # plt.plot(df['predicted_val'])
    dtemp     = df[(df['age17']==1)&(df['insch']==True)]
    dtemp.loc[:,'Npred'] = dtemp[2017] * (1-dtemp['predicted_val'])
    N2017 = np.sum(dtemp['Npred'])
    
    dtemp     = df[(df['age18']==1)&(df['insch']==True)]
    N2018 = np.sum(dtemp[2017])
    
    dis = (N2018-N2017)**2
    
    print(dis**0.5)
    return dis


factor = minimize(f,1.0)
factor = factor.x
factor = factor[0]

df, transparam = prepare()
transparam['age17'] = factor*transparam['age17'] 
for keys in transparam.keys():
    df['predicted_val'] += df[keys]*transparam[keys]
df['predicted_val'] = 1 /(1+np.exp(-df['predicted_val']))
df = df.groupby(['age']).mean()
plt.plot(df['predicted_val'])

df, transparam = prepare()
transparam['age17'] = 1*transparam['age17'] 
for keys in transparam.keys():
    df['predicted_val'] += df[keys]*transparam[keys]
df['predicted_val'] = 1 /(1+np.exp(-df['predicted_val']))
df = df.groupby(['age']).mean()
plt.plot(df['predicted_val'])
plt.show()

df, transparam = prepare()
transparam['constant'] = transparam['age17']
transparam.pop('age17')

# change for saving the ouput
for age in range(18,36):
    transparam['age'+str(age)] = transparam['age'+str(age)] -factor*transparam['constant']
transparam['constant'] = factor * transparam['constant']
transparam['var'] = 'schldone'


df = pd.DataFrame(transparam, index=[0])
df = (df.T)
print (df)
df.to_excel('trans_schldone_adj.xlsx')














