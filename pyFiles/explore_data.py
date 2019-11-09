import pyFiles.Input as inp
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
data = pd.read_csv("data/Simulation.csv")

#Plot showing major factors that survived 
surv = data.ix[:,'survive']
admitted = data.loc[surv == 1]
not_admitted = data.loc[surv == 0]

plt.scatter(admitted.ix[:,'pos_(2,1,0)'],admitted.ix[:,'vel_(2,1,0)'], label='Survived')
plt.legend()
plt.scatter(not_admitted.ix[:,'pos_(2,1,0)'],not_admitted.ix[:,'vel_(2,1,0)'],label = 'Not Survived')
plt.xlabel('pos_(2,1,0)')
plt.ylabel('vel_(2,1,0)')
plt.legend()
plt.show()
plt.savefig('figures/ScatterPlot1')

plt.scatter(admitted.ix[:,'pos_(2,1,0)'],admitted.ix[:,'mass_(1)'], label='Survived')
plt.legend()
plt.scatter(not_admitted.ix[:,'pos_(2,1,0)'],not_admitted.ix[:,'mass_(1)'],label = 'Not Survived')
plt.xlabel('pos_(2,1,0)')
plt.ylabel('mass_(1)')
plt.legend()
plt.show()
plt.savefig('figures/ScatterPlot3')

plt.scatter(admitted.ix[:,'pos_(2,1,0)'],admitted.ix[:,'survive'], label='Survived')
plt.legend()
plt.scatter(not_admitted.ix[:,'pos_(2,1,0)'],not_admitted.ix[:,'survive'],label = 'Not Survived')
plt.xlabel('pos_(2,1,0)')
plt.ylabel('survive')
plt.legend()
plt.show()
plt.savefig('ScatterPlot4')


data_1 = pd.read_csv("data/Simulation.csv")

data_tmp = data.groupby("treatmentN").sum()/16

data = data.groupby("treatmentN").first()

data.ix[:,'survive'] = data_tmp.ix[:,'survive']

print(list(data.columns))

data.head()

sns.countplot(x='survive',data=data,palette='hls')
plt.show()
plt.savefig('count_plot')

data['survive'].value_counts()

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
plt.savefig('figures/Sample_Sequence_Plot')

#data_final_vars=data.columns.values.tolist()
#y = ['treatmentN', 'monteCarloN', 'eject', 'collide', 'nSteps', 'survive', 'pos_(0,1,0)', 'pos_(1,1,0)', 'pos_(0,2,0)', 'pos_(1,2,0)', 'pos_(2,2,0)', 'vel_(0,1,0)', 'vel_(1,1,0)', 'vel_(0,2,0)', 'vel_(1,2,0)', 'vel_(2,2,0)', 'vel_(0,0,0)', 'vel_(1,0,0)', 'vel_(2,0,0)', 'runTime', 'pos_(0,0,-1)', 'vel_(0,0,-1)', 'pos_(0,1,-1)', 'vel_(0,1,-1)', 'pos_(0,2,-1)', 'vel_(0,2,-1)', 'pos_(1,0,-1)', 'vel_(1,0,-1)', 'pos_(1,1,-1)', 'vel_(1,1,-1)', 'pos_(1,2,-1)', 'vel_(1,2,-1)', 'pos_(2,0,-1)', 'vel_(2,0,-1)', 'pos_(2,1,-1)', 'vel_(2,1,-1)', 'pos_(2,2,-1)', 'vel_(2,2,-1)']

#X=[i for i in data_final_vars if i not in y]

x = data[X]
y = data['survive']
x = data[list(inp.controlFactors.keys())]

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression

#pdb.set_trace()

#This section use the RFE method to help determine significant factor for the
#surrogate model 


#rfe_1 looks for the leading significant factor that determines the
#survival of the orbit 
logreg = LogisticRegression()
rfe_1 = RFE(logreg,1)
rfe_1 = rfe_1.fit(x,y)
print(rfe_1.support_)
print(rfe_1.ranking_)


rfe_2 = RFE(logreg,2)
rfe_2 = rfe_2.fit(x,y)
print(rfe_2.support_)
print(rfe_2.ranking_)

rfe_3 = RFE(logreg,3)
rfe_3 = rfe_3.fit(x,y)
print(rfe_3.support_)
print(rfe_3.ranking_)

#This looks at the saturated model that accounts all of them
#logreg.fit(x,y)
#print('Coefficients:')
#print(logreg.coef_)
#print('Intercept')
#print(logreg.intercept_)

#This looks at a single factor 
cols = ['pos_(2,1,0)']
xi = data[cols].values.reshape(-1,1)
yi = data['survive'].values.reshape(-1,1)
logreg.fit(xi,np.ravel(yi.astype(int)))
print(logreg.coef_)
print(logreg.intercept_)

#pdb.set_trace()
plt.scatter(xi,yi)
plt.xlabel('pos_(2,1,0)')
plt.ylabel('Probability of Survival')
plt.scatter(xi,logreg.predict_proba(xi)[:,1])
plt.show()
plt.savefig('figures/LogisticRegressionSingleFactor')

x = np.linspace(-10,10,40).reshape(40,1)
y = 1/(1+np.exp(-(logreg.intercept_+logreg.coef_*x)))
y.reshape(40,1)
plt.plot(x,y)
plt.show()
plt.savefig('Logistic Regression Single Factor Curve')

#import statsmodels.api as sm
#logit_model_all=sm.Logit(y,x)
#result=logit_model_all.fit()
#print("All features accounted!")
#print(result.summary2())
#print(np.exp(result.params))

'''
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
'''


