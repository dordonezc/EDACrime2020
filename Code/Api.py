## Api
import pandas as pd 
import os
import re
import requests
import geopandas as gpd
import pickle
os.chdir("C:/Users/dordo/Documents/Daniel/LSE/ST 445/Proyecto")

##--------------------------------------------------------------##
## Load information on MSOA to use API 
data_MSOA = gpd.read_file("statistical-gis-boundaries-london/ESRI/MSOA_2011_London_gen_MHW.shp")
data_MSOA = data_MSOA.to_crs(epsg=4326)

##---------------------------------------------------------------------------##
## Functions used to make Api request: 
def get_coords(x):
    """ Takes a polygon/multipolygon as given by a geometry
    and returns the coordinate sequence"""
    try:
        coords = [item.exterior.coords for item in x]
    except:
        coords = [x.exterior.coords]
    return coords

def get_frisk_data(point, date, max_val = 3500):
    """ Takes a polygon coordinates as parsed with the get_coords function
    and a date return a count of frisks made in the polygon for that date
    according to age"""
    base = "https://data.police.uk/api/stops-street?poly={}&date={}"
    poly_coords = ":".join([str(val[1]) + "," + str(val[0]) for val in list(point)])
    response = requests.get(base.format(poly_coords[:max_val], date))
    content = response.json()
    comp = [item["age_range"] for item in content]
    counts = pd.Categorical(comp, categories = ["10-17", "18-24", "25-34", "over 34"]).value_counts()
    return counts
##--------------------------------------------------------------------------##
def frisk_to_pandas(date, save_list, index_list):
    """ Takes a date a list with MSOA polygons|Multipolygons along with the 
    index list to represent all the polygons in one of the multypoligons one. 
    Returns pandas dataframe for the frisk data
    and pickle file is generated in the path with the corresponding month.""" 
    ## Request api data
    serie = pd.Series()
    for index, x in enumerate(save_list):
        serie = pd.concat([serie, get_frisk_data(x, date)])
    
    ## Create data with MSOA index
    fix_index = []
    for val in index_list:
        fix_index.extend([val] * 4)
    fix_index = pd.DataFrame({"MSOA ID": fix_index})
    
    ## Merge Frisk data with MSOA 
    my_df = pd.concat([serie.reset_index(),fix_index], axis=1)
    final_df = my_df.pivot(index="MSOA ID", columns="index", values=0)
    final_df.columns = pd.Index(list(final_df.columns))
    
    ## Create ID for multipolygons in order to collapse
    p = re.compile("[0-9]+")
    split = [(x,p.match(x).group()) for x in final_df.index]
    match_tab = pd.DataFrame({"Group":[val[1] for val in split],
                              "MSOA ID": [val[0] for val in split]})
    final_df.reset_index(inplace=True)
    
    ## Collapse by Polygon/Multipolygon
    final_dfm = pd.merge(final_df, match_tab).groupby("Group").agg(sum)
    
    ## Paste with MSOA names
    MSOA_names = data_MSOA[["MSOA11NM"]].reset_index()
    final_dfm.reset_index(inplace=True)
    final_dfm["Group"] = final_dfm.Group.astype(int)
    save_df = pd.merge(MSOA_names,final_dfm, right_on="Group", left_on="index")
    save_df.drop(["index","Group"],axis=1, inplace=True)
    save_df["Month"] = date[-1]
    
    ## Save to pickle 
    filename = "DataFrisk" + date[-1] + ".p"
    #pickle.dump(save_df, open(filename, "wb"))
    return save_df


## Convert polygons in geometry to coordinate lists
save_list, index_list = [], []
for index, item in enumerate(data_MSOA.geometry):
    res = get_coords(item)
    save_list.extend(res)
    ## Keep index for multypoligons
    index_list.extend([str(index) + "-" + str(x) for x in range(len(res))])

dates = ["2020-0" + str(d) for d in range(1,10)]
final_list = [frisk_to_pandas(x,save_list,index_list) for x in dates]
all_frisk = pd.concat(final_list)
pickle.dump(save_df, open("AllFrisk.p", "wb"))