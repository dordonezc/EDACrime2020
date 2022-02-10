import pandas as pd 
import os
import numpy as np
import pickle

os.chdir("C:/Users/dordo/Documents/Daniel/LSE/ST 445/Proyecto")

##--------------------------------------------------------------------------##
## Initial Cleaning
## Read data 
data = pd.read_csv("DataProject.csv")

## Drop Id columns
data.drop(["Id","Unnamed: 0"],axis=1,inplace=True)

## Rename Columns
data.rename({"Crime type":"Crime", "Last outcome category":"Category"},axis=1,
            inplace=True)

## Handling of missing values
# Note that missing in Category means that there was no outcome
data.isnull().sum()
bfill = data.groupby("Crime").Category.nunique()
data.fillna("No further investigation",inplace=True)

## Check filled missing values by group
afill = data.groupby("Crime").Category.nunique()
check = pd.merge(bfill.reset_index(),afill,on="Crime")
check
# Note that all missing were on the Anti Social behaviour crime

## Create Lockdown variable
conds = [data.Month.lt(4), data.Month.lt(7), data.Month.lt(10)]
data['Covid'] = np.select(conds, ["PreLockdown","Lockdown","PostLockdown"])

## Replace Month with complete Date
data['Date'] = pd.to_datetime(["2020-" + str(x) + "-01" for x in data.Month])

## Convert categorical variables to category
for col in ['Location', 'LSOA name','Crime', 'Category', 'Covid']:
    data[col] = data[col].astype('category')

## Reorder|Rename categories
data['Covid'].cat.reorder_categories(['PreLockdown', 'Lockdown', 'PostLockdown'], 
                                     inplace=True)
data['Location'].cat.rename_categories({'City of London ':'City of London',
                                    'Metropolitan  Service':'Metropolitan Service'},
                                       inplace=True)
## Lump low counts (Weapon Possesion)
need = data['Crime'].value_counts().index[-1:-3:-1]
data['Crime'] = np.where(~data['Crime'].isin(need), data['Crime'], 'Other crime')

## Delete non-using variables
del bfill, afill, check, conds, need

## Save to pickle 
pickle.dump(data, open("DataClean.p", "wb"))
