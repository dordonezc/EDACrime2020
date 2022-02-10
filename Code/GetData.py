## Import Police Data
import os 
import pandas as pd
import numpy as np
os.chdir("C:/Users/dordo/Documents/Daniel/LSE/ST 445/Proyecto")

## Define function to clean monthly data
def quick_clean(month, loc):
    """ This function takes a month and a location as in the police data syntax
    returns the dataset for that month in that location"""
    path = "2020-" + month + "/2020-" + month + "-"  + loc + "-street.csv"
    data = pd.read_csv(path)
    ## Generate numeric ID 
    data["Id"] = range(data.shape[0])
    ## Generate Year/Month
    data[['Year','Month']] = data.Month.str.split("-",expand=True,)
    ## Change Location
    data['Location'] = data['Reported by'].str.replace("Police",repl="")
    ## Keep only relevant variables
    data.drop(["Reported by","Falls within","Crime ID", "Context", "Year"],
              axis=1, inplace=True)
    ## Drop data without location
    data = data[~np.isnan(data.Latitude)]
    return data

## Define locations and months to be used
locs = ["city-of-london", "metropolitan"]
months = ["0" + str(num) for num in range(1,10)]
iter_tup = tuple((month,loc) for month in months for loc in locs)

## Load data and save to csv
data_police = [quick_clean(*args) for args in iter_tup]
final_data = pd.concat(data_police)
final_data.to_csv("DataProject.csv")
