from __future__ import division 

import pandas as pd
import numpy as np
import pdb
from sklearn import preprocessing
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import seaborn as sns

plt.rc("font",size=14)
sns.set(style="white")
sns.set(style="whitegrid",color_codes=True)

data = pd.read_csv("Simulation.csv")

data_1 = pd.read_csv("Simulation.csv")

data_tmp = data.groupby("treatmentN").sum()/16

data = data.groupby("treatmentN").first()

data.ix[:,'survive'] = data_tmp.ix[:,'survive']

print(list(data.columns))

data.head()

sns.countplot(x='survive',data=data,palette='hls')
plt.show()
plt.savefig('count_plot')

data['survive'].value_counts()

count_no_sur = len(data[data['survive']==0])
count_sur = len(data[data['survive']==1])
pct_of_no_sur = count_no_sur/(count_no_sur+count_sur)
print("percent of no survival is ", pct_of_no_sur*100, '%')
pct_of_sur = count_sur/(count_no_sur+count_sur)
print("percent of survival is ", pct_of_sur*100, '%')

treatments = data_1['treatmentN']
survivals = data_1['survive']
surv_avg = data.ix[:,'survive'].sum()/150
surv_avg = [surv_avg]*treatments.size
surv_avg_ind = data.ix[:,'survive']
treatments_ind = pd.DataFrame({'treatments':range(1,151)})
line1,=plt.plot(treatments,survivals,'.',label="MC Treatments")
line2,=plt.plot(treatments,surv_avg,'-',label="Overall Avg")
line3,=plt.plot(treatments_ind,surv_avg_ind,'*',label="MC Avg")
plt.legend(handles=[line1,line2,line3],loc='lower right')
plt.xlabel('Treatments')
plt.ylabel('Probability of Survive')
plt.title('Sample Sequence Probability 3 Star Orbit Stability')
plt.show()
plt.savefig('Sample_Sequence_Plot')

data_final_vars=data.columns.values.tolist()
y = ['treatmentN', 'monteCarloN', 'eject', 'collide', 'nSteps', 'survive', 'pos_(0,1,0)', 'pos_(1,1,0)', 'pos_(0,2,0)', 'pos_(1,2,0)', 'pos_(2,2,0)', 'vel_(0,1,0)', 'vel_(1,1,0)', 'vel_(0,2,0)', 'vel_(1,2,0)', 'vel_(2,2,0)', 'vel_(0,0,0)', 'vel_(1,0,0)', 'vel_(2,0,0)', 'runTime', 'pos_(0,0,-1)', 'vel_(0,0,-1)', 'pos_(0,1,-1)', 'vel_(0,1,-1)', 'pos_(0,2,-1)', 'vel_(0,2,-1)', 'pos_(1,0,-1)', 'vel_(1,0,-1)', 'pos_(1,1,-1)', 'vel_(1,1,-1)', 'pos_(1,2,-1)', 'vel_(1,2,-1)', 'pos_(2,0,-1)', 'vel_(2,0,-1)', 'pos_(2,1,-1)', 'vel_(2,1,-1)', 'pos_(2,2,-1)', 'vel_(2,2,-1)']

X=[i for i in data_final_vars if i not in y]

x = data[X]
y = data['survive']


from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression

pdb.set_trace()

logreg = LogisticRegression()
rfe_1 = RFE(logreg,1)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)
logreg.fit(x,y)
print('Coefficients:')
print(logreg.coef_)

rfe_1 = RFE(logreg,2)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)

rfe_1 = RFE(logreg,3)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)

rfe_1 = RFE(logreg,4)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)

rfe_1 = RFE(logreg,8)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)

import statsmodels.api as sm
logit_model_all=sm.Logit(y,x)
result=logit_model_all.fit()
print("All features accounted!")
print(result.summary2())

from scipy.special import expit 

x = data['pos_(2,1,0)']

logit_model_1=sm.Logit(y,x)
result=logit_model_1.fit()
print("Single Feature accounted!")
print(result.summary2())


cols = ['pos_(2,1,0)','mass_(1)','vel_(2,1,0)']
x = data[cols]

logit_model_3=sm.Logit(y,x)
result=logit_model_3.fit()
print("3 Features accounted!")
print(result.summary2())

logreg.fit(x,y)
print(logreg.coef_)
print(logreg.intercept_)




