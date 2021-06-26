from logging import error
from math import log
from re import X
import warnings
import ast

from matplotlib.colors import Normalize
from numpy.core.fromnumeric import mean, shape
from pandas.io.parsers import read_csv
from scipy.sparse.construct import rand
from sklearn.utils import shuffle
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
warnings.simplefilter(action='ignore', category=FutureWarning)


import random
from threading import Thread
from numpy import NaN, empty, nan, number
import pandas as pd
import difflib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import seaborn as sns
import numpy as np
from sklearn import preprocessing



from pandas.core.dtypes.missing import notnull
from pandas.io.pytables import incompatibility_doc
from python_scripts.getDatabase_part_1 import get_database_from_url, runCommand
from python_scripts.connect_db import combine_csv
from python_scripts.export_from_battle import get_all_battles_from_page, get_all_battles_from_special_page
from python_scripts.geopandas_plot import plot_world_special_treatment, plot_world_sum, plot_world_video,plot_world, world
from python_scripts.seaborn import MultiGraph


#This is the main code for my dataScince project.
months = ['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#Helper Methods:
def country_edit_name(df,column):
    countries = world.name.tolist()
    for idx, location in enumerate(df[column]):
        new_location = ""
        res = difflib.get_close_matches(str(location), countries)
        if len(res) != 0:
                new_location = res[0]
        else: 
                new_location = location
        df.loc[idx, column] = new_location

#This method takes a row from country_df, and check if the country is listed
# in column inside df. If so, it add it to the string
def translate_row(df, column, row):
    war_list_for_country = ""
    for idx, country_set in enumerate(df[column]):
        if row["country"] in country_set:
            war_list_for_country += str(idx) + ","
    
    return war_list_for_country

#This method is to clean all Outliers
def removeOutliers(data, col):
    Q3 = np.quantile(data[col], 0.75)
    Q1 = np.quantile(data[col], 0.25)
    IQR = Q3 - Q1
     
    print("IQR value for column %s is: %s" % (col, IQR))
    global outlier_free_list
    global filtered_data
     
    lower_range = Q1 - 1.5 * IQR
    upper_range = Q3 + 1.5 * IQR
    outlier_free_list = [x for x in data[col] if (
        (x > lower_range) & (x < upper_range))]
    filtered_data = data.loc[data[col].isin(outlier_free_list)]

#Stage 1.a - Get databases from sites via crawling using selenium. 
#In here, we get all the information from -3250 to preasnt year about:
#war_url,start_year,finish_year,winner_list,losser_list,location,casualties_A,casualties_B,strength_A,strength_B,terror
#casualties_A - Number of death, missing pepole, wounded and much more in team a
#casualties_B - Number of death, missing pepole, wounded and much more in team a
#strength_A - Number of man, woman, animals, aircrafts, and much more that tought for team A
#strength_B - Number of man, woman, animals, aircrafts, and much more that tought for team B
#terror - True if the war is terror related.
def createDatabases():
    #Get all wars.
    number_of_threads = 8
    threads = []

    wikipedia_links_for_wars = ["https://en.wikipedia.org/wiki/List_of_wars:_before_1000","https://en.wikipedia.org/wiki/List_of_wars:_1000%E2%80%931499","https://en.wikipedia.org/wiki/List_of_wars:_1500%E2%80%931799","https://en.wikipedia.org/wiki/List_of_wars:_1800%E2%80%931899","https://en.wikipedia.org/wiki/List_of_wars:_1900%E2%80%931944","https://en.wikipedia.org/wiki/List_of_wars:_1945%E2%80%931989","https://en.wikipedia.org/wiki/List_of_wars:_1990%E2%80%932002","https://en.wikipedia.org/wiki/List_of_wars:_2003%E2%80%93present"]
    database_names_for_wars = ["before_1000","1000–1499","1500–1799","1800–1899","1900–1944","1945–1989","1990–2002","2003–present"]

    wikipedia_links_for_battles = ["https://en.wikipedia.org/wiki/List_of_battles_before_301","https://en.wikipedia.org/wiki/List_of_battles_301%E2%80%931300","https://en.wikipedia.org/wiki/List_of_battles_1301%E2%80%931600"]
    database_names_for_battles = ["before_301_battle","301-1300_battle","1301-1600_battle"]

    wikipedia_links_for_special_battles = ["https://en.wikipedia.org/wiki/List_of_battles_1601%E2%80%931800", "https://en.wikipedia.org/wiki/List_of_battles_1801%E2%80%931900", "https://en.wikipedia.org/wiki/List_of_battles_1901%E2%80%932000"]
    database_names_for_special_battles = ["1601-1800_battle","1801-1900_battle","1901-2000_battle"]

    for num in range(number_of_threads):
        thread = Thread(target=get_database_from_url, args=(wikipedia_links_for_wars[num],database_names_for_wars[num],))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join
    
    
    #Same for battles
    number_of_threads = 3 # twice 2 for special wars
    threads = []
    
    
    for num in range(number_of_threads):
        thread = Thread(target=get_all_battles_from_page, args=(wikipedia_links_for_battles[num],database_names_for_battles[num],))
        thread_special = Thread(target=get_all_battles_from_special_page, args=(wikipedia_links_for_special_battles[num],database_names_for_special_battles[num],))
        thread.start()
        thread_special.start()
        threads.append(thread)
        threads.append(thread_special)

    for thread in threads:
        thread.join
    

#Stage 1.b - Combine the csv files into one big csv. 
def run_combine_csv():
    combine_csv()
    
#Stage 1.c - Build countries dataframe
def create_countries_dataframe():
    border_df = pd.read_csv("Databases/countries/borders.csv", names=["country", "border_length", "number_of_borders"])
    coastline_df = pd.read_csv("Databases/countries/coast_line.csv", names=["country", "coast_length"])
    religion_df = pd.read_csv("Databases/countries/religon.csv", names=["country", "religon"])
    temp_df = pd.read_csv("Databases/countries/temp.csv", names=["country", "temp"])
    sea_level_df = pd.read_csv("Databases/countries/sea_level.csv", names=["country", "sea_level"])
    
    border_df.sort_values(by="country")
    coastline_df.sort_values(by="country")
    religion_df.sort_values(by="country")
    temp_df.sort_values(by="country")
    sea_level_df.sort_values(by="country")

    country_edit_name(border_df,"country")
    country_edit_name(coastline_df,"country")
    country_edit_name(religion_df,"country")
    country_edit_name(temp_df,"country")
    country_edit_name(sea_level_df,"country")
    

    border_df = border_df.groupby(["country"], as_index=False)["border_length", "number_of_borders"].sum()
    coastline_df = coastline_df.groupby(["country"], as_index=False)["coast_length"].sum()
    #temp_df = temp_df.groupby(["country"], as_index=False)["temp"].sum()
    #sea_level_df = sea_level_df.groupby(["country"], as_index=False)["sea_level"].sum()
    

    country_df = pd.merge(coastline_df,religion_df,on="country",how="left")
    country_df = pd.merge(country_df, border_df, on="country", how="left")
    country_df = pd.merge(country_df, temp_df, on="country", how="left")
    country_df = pd.merge(country_df, sea_level_df, on="country", how="left")
    
    country_df.to_csv("country_df.csv")


    return country_df

#Stage 1.d - Clean nan values for countries
def clean_country(df):
    df["temp"] = df["temp"].str.replace('−', '-')
    df['temp'] = df['temp'].astype(float)
    df["sea_level"] = df["sea_level"].str.replace(',', '')
    df['sea_level'] = df['sea_level'].astype(float)
    values = {"coast_length" : df.coast_length.median(),
     "religon" : "Unknown",
      "border_length" : df.border_length.median(),
       "number_of_borders" : df.number_of_borders.median(),
        "temp" : df.temp.median(),
         "sea_level" : df.sea_level.median()}
    df["religon"] = df["religon"].replace("Roman", "Roman Chatolic")
    df["border_length"] = df["border_length"].replace(0, 1)
    df["water_land_ratio"] = df.apply(lambda row: float(row.coast_length) / float(row.border_length), axis = 1 )
    df.fillna(value=values, inplace=True)

def extract_year(x):
    try:
        return pd.to_datetime(x).year
    except:
        return x

#Stage 2.a - In here, we are going to do sevral things - 
# 1. Get rid of all raws that contain # in there URL beacuse those are'nt real wars nor battles but
#   some unneccery information. Plus, get rid of all raws with -1 and unknown for all stregnth and casualties 
#
# 2. Set every battle winner, losser and location into string and not list
#
#
# 3. Insert inside location value with NaN the value of either winner or losser information 
#
# 4. Add non-state to raws in which the winner or losser side was'nt a state.
def intial_cleanup(df):
    #Drop all wars with # in thier URL 
   
    df.drop(df[df["war_url"].str.contains("#")].index, inplace=True)
   
    #Clear my columns 
    df['location'] = df['location'].astype(str).str.strip('[]').str.replace("'",'').str.replace('[','').str.replace(']','').str.replace('\d+', '')
    df['winner_list'] = df['winner_list'].astype(str).str.strip('[]').str.replace("'",'').str.replace('[','').str.replace(']','').str.replace('\d+', '')
    df['losser_list'] = df['losser_list'].astype(str).str.strip('[]').str.replace("'",'').str.replace('[','').str.replace(']','').str.replace('\d+', '')

    #Drop all raws that dont include any data
    df.drop(df[df["casualties_A"].str.contains("-1")].index, inplace=True)
    df.drop(df[df["casualties_B"].str.contains("-1")].index, inplace=True)
    df.drop(df[df["strength_A"].str.contains("-1")].index, inplace=True)
    df.drop(df[df["strength_B"].str.contains("-1")].index, inplace=True)
    
    df.drop(df[df["casualties_A"].str.contains("unknown")].index, inplace=True)
    df.drop(df[df["casualties_B"].str.contains("unknown")].index, inplace=True)
    df.drop(df[df["strength_A"].str.contains("unknown")].index, inplace=True)
    df.drop(df[df["strength_B"].str.contains("unknown")].index, inplace=True)
    
    #Drop all wars without location,winner and lossers
    df.drop(df[(df.location.isnull()) & (df.winner_list.isnull()) & (df.losser_list.isnull())].index, inplace=True)

    #Replacing all empty location to combonation of winner and lossers
    df.location = df.location.fillna(df.winner_list.str.cat(df.losser_list, sep=',')) #In case winner_list and losser_list is'nt NaN
    df.location = df.location.fillna(df.winner_list) #In case losser_list empty
    df.location = df.location.fillna(df.losser_list) #In case winner_list empty
    
    #Fill empty value of winner_list and losser_list with non-state 
    values = {'winner_list': 'non-state',
    'losser_list': 'non-state'}
    df = df.fillna(value=values)


#2.b This is a special function only to treat the years part   
def special_treatment_for_years(df):
    bc = df['start_year'].str.contains('BC')
    df.loc[bc,'start_year'] = '-'+df.loc[bc,'start_year']

    bc = df['finish_year'].str.contains('BC')
    df.loc[bc,'finish_year'] = '-'+df.loc[bc,'finish_year']

    val = df['start_year'].str.extract('(-?[0-9]+)').fillna('2021')
    df['start_year'] = df['start_year'].str.extract('(\d{4})').fillna(val)
    df['start_year'] = df['start_year'].apply(lambda x: extract_year(x))

    val = df['finish_year'].str.extract('(-?[0-9]+)').fillna('2021')
    df['finish_year'] = df['finish_year'].str.extract('(\d{4})').fillna(val)
    df['finish_year'] = df['finish_year'].apply(lambda x: extract_year(x))
    
#Stage 2.c - Add new columns to the dataframe:
#
# 1. Turn numric values columns to numric and not string
#
# 2. Create new columns based on other
def build_up(df):
    #Turn columns into numric
    df['start_year'] = pd.to_numeric(df['start_year'],errors='coerce')
    df['finish_year'] = pd.to_numeric(df['finish_year'],errors='coerce')
    df['casualties_A'] = pd.to_numeric(df['casualties_A'],errors='coerce')
    df['casualties_B'] = pd.to_numeric(df['casualties_B'],errors='coerce')
    df['strength_A'] = pd.to_numeric(df['strength_A'],errors='coerce')
    df['strength_B'] = pd.to_numeric(df['strength_B'],errors='coerce')
    df['war_or_battle'] = pd.to_numeric(df['war_or_battle'],errors='coerce')


    #Add death ratio = Side_a / Side_b
    df["death_ratio"] = df.apply(lambda row: float(row.casualties_A) / float(row.casualties_B), axis = 1 )
    df.drop(df[df["death_ratio"] >= 1000].index, inplace = True)
    df.drop(df[df["death_ratio"] <= 0.0001].index, inplace = True)

    #Add army ratio = Side_a / Side_b
    df["army_ratio"] = df.apply(lambda row: float(row.strength_A) / float(row.strength_B), axis = 1 )
    df.drop(df[df["army_ratio"] >= 1000].index, inplace = True)
    df.drop(df[df["army_ratio"] <= 0.0001].index, inplace = True)

    #Add side_a ratio = Side_a_casualties / Side_a_strength
    df["side_a_ratio"] = df.apply(lambda row: float(row.casualties_A) / float(row.strength_A), axis = 1 )
    df.drop(df[df["side_a_ratio"] >= 1000].index, inplace = True)
    df.drop(df[df["side_a_ratio"] <= 0.0001].index, inplace = True)

    #Add side_a ratio = Side_a_casualties / Side_a_strength
    df["side_b_ratio"] = df.apply(lambda row: float(row.casualties_B) / float(row.strength_B), axis = 1 )
    df.drop(df[df["side_b_ratio"] >= 1000].index, inplace = True)
    df.drop(df[df["side_b_ratio"] <= 0.0001].index, inplace = True)

#stage 2.d - Normalize certien data
def normalize(df):
    cols_to_norm = ['casualties_A','casualties_B','strength_A','strength_B']
    df[cols_to_norm] = df[cols_to_norm].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

#stage 2.e - add population to the list
def population(df):
    Population = pd.read_csv('Databases/population.csv', names=["Year","population"]) 
    Population.info()
    new_df = pd.merge_asof(df.sort_values(by=['start_year']),Population.sort_values(by=["Year"]),left_on='start_year',right_on='Year').drop('Year',1)
    return new_df

#stage 2.f - Add population ratio
def population_ratio(df):
    df['population'] = pd.to_numeric(df['population'],errors='coerce')

    #Add death ratio = population / Side_a
    df["population_death_side_a_ratio"] = df.apply(lambda row: float(row.population) / (float(row.casualties_A) + 1), axis = 1)

    #Add death ratio = population / Side_b
    df["population_death_side_b_ratio"] = df.apply(lambda row: float(row.population) / (float(row.casualties_B) + 1), axis = 1)

    #Add death ratio = population / Side_a
    df["population_army_side_a_ratio"] = df.apply(lambda row: float(row.population) / (float(row.strength_A) + 1), axis = 1)
    
    #Add death ratio = population / Side_a
    df["population_army_side_b_ratio"] = df.apply(lambda row: float(row.population) / (float(row.strength_B) + 1), axis = 1)

#stage 2.g - replace countries name into readable names for geoPandas
def replace_countries_name(df,column):
    countries = world.name.tolist()
    for idx, location in enumerate(df[column]):
        new_location = ""
        for loca in location.split(','):
            res = difflib.get_close_matches(str(loca), countries)
            if len(res) != 0:
                new_location = new_location + res[0] + ","
            else: 
                new_location = new_location + loca + ","
        df.loc[idx, column] = new_location

#stage 2.h - Build up for countries df using the war df
def build_up_for_countries(df, country_df):
    country_df["winning_wars"] = country_df.apply(lambda row: translate_row(df,"winner_list",row), axis=1)
    country_df["lost_wars"] = country_df.apply(lambda row: translate_row(df,"losser_list",row), axis=1)
    country_df["wars_in_country"] = country_df.apply(lambda row: translate_row(df,"location",row), axis=1)  

    #In here, we will sum up the number of wars in which a country:
    # participate
    # won 
    # lost
    # host - wars in her area
    # imperialism - wars she won outside her country 
    # deimperialsm - wars she lost inside her country
    state_wars_imperial = []
    state_wars_deimperial = []
    state_wars_participate = []
    state_number_of_winnings = []
    state_number_of_lossing = []
    state_number_of_wars_at_location = []
    for idx, state in enumerate(country_df["country"]):
        imperialism = 0
        deimperialism = 0

        #Wars won per state
        if country_df.iloc[idx]["winning_wars"] == nan:
            winning = 0
        else:
            winning = float(len(str(country_df.iloc[idx]["winning_wars"]).split(',')) - 1)
            if country_df.iloc[idx]["wars_in_country"] != nan:
                winning_wars = str(country_df.iloc[idx]["winning_wars"]).split(',')[:-1]
                inside_wars = str(country_df.iloc[idx]["wars_in_country"]).split(',')[:-1]
                for war in winning_wars:
                    if war not in inside_wars:
                        imperialism += 1
        
        #Wars loses per state
        if country_df.iloc[idx]["lost_wars"] == nan:
            lossing = 0
        else:
            lossing = float(len(str(country_df.iloc[idx]["lost_wars"]).split(',')) - 1)
            if country_df.iloc[idx]["wars_in_country"] != nan:
                lossing_wars = str(country_df.iloc[idx]["lost_wars"]).split(',')[:-1]
                inside_wars = str(country_df.iloc[idx]["wars_in_country"]).split(',')[:-1]
                for war in lossing_wars:
                    if war in inside_wars:
                        deimperialism += 1

        #Wars at location per state
        if country_df.iloc[idx]["wars_in_country"] == nan:
            location = 0
        else:
            location = float(len(str(country_df.iloc[idx]["wars_in_country"]).split(',')) - 1)
        
        state_wars_imperial.append(imperialism)
        state_wars_deimperial.append(deimperialism)
        state_number_of_winnings.append(winning)
        state_number_of_lossing.append(lossing)
        state_number_of_wars_at_location.append(location)
        state_wars_participate.append(winning+lossing)
    
    battles_in_country = []
    #Collecting terror participent and terror in location
    for idx, state in enumerate(country_df["country"]):
        if country_df.iloc[idx]["wars_in_country"] == nan:
            battles_in_country.append(0)
        else:
            sum=0
            inside_wars = str(country_df.iloc[idx]["wars_in_country"]).split(',')[:-1]
            for war in inside_wars:
                if df.iloc[int(war)]["war_or_battle"] == 1:
                    sum+=1
            battles_in_country.append(sum)
        

    country_df["wars_victory"] = state_number_of_winnings
    country_df["wars_loses"] = state_number_of_lossing
    country_df["total_wars_participate"] = state_wars_participate
    country_df["wars_inside_country"] = state_number_of_wars_at_location
    country_df["imperialism_wars"] = state_wars_imperial
    country_df["deimperialism_wars"] = state_wars_deimperial
    country_df["battles_in_country"] = battles_in_country

#stage 3.a Create simple world graphs:
#The df contain only name of country and information you want dispay about it
def world_graph(df, column, cmapR="rainbow"):
    plot_world(df,column, cmapR)

#stage 3.b Scatter maps
def scatter_values_two_dim(df, xais="", yais="", cmap="coral"):
    df.plot.scatter(x=xais, y=yais,c=cmap)
    plt.show()


#stage 4.a Building X dataset:
def build_X_total(country_df):
    #X is the combained files from before without any drops
    X = pd.read_csv("ML-data/X.csv")
    X['location'] = X.location.str.rstrip(',').str.split(',')
    X = X.explode('location')
    world_countries = world.name.tolist()
    #The Values in which X is holding:
    country_name = [] 
    coast_length = []
    border_length = []
    sea_level = []
    number_of_borders = []
    avg_temp = []

    location_country_name = [] 
    location_coast_length = []
    location_border_length = []
    location_sea_level = []
    location_number_of_borders = []
    location_avg_temp = []

    label = [] # Won or lost (0/1 Lost/Won)
    
    for idx, state in enumerate(country_df["country"]):
        for idx_X, winners in enumerate(X["winner_list"]):
            if state in winners:
                country_name.append(state)
                coast_length.append(country_df.iloc[idx]["coast_length"])
                border_length.append(country_df.iloc[idx]["border_length"])
                sea_level.append(country_df.iloc[idx]["sea_level"])
                number_of_borders.append(country_df.iloc[idx]["number_of_borders"])
                avg_temp.append(country_df.iloc[idx]["temp"])
                label.append(1)

                #Add winners location details
                res = difflib.get_close_matches(str(X.iloc[idx_X]["location"]), world_countries)
                if(len(res) > 0):
                    country_indexes = country_df.index[country_df["country"] == res[0]].tolist()
                    if (len(country_indexes) > 0):
                        country_index = country_indexes[0]
                        location_country_name.append(res[0]) 
                        location_coast_length.append(country_df.iloc[country_index]["coast_length"])
                        location_border_length.append(country_df.iloc[country_index]["border_length"])
                        location_sea_level.append(country_df.iloc[country_index]["sea_level"])
                        location_number_of_borders.append(country_df.iloc[country_index]["number_of_borders"])
                        location_avg_temp.append(country_df.iloc[country_index]["temp"])
                    else:
                        location_country_name.append(-1) 
                        location_coast_length.append(-1)
                        location_border_length.append(-1)
                        location_sea_level.append(-1)
                        location_number_of_borders.append(-1)
                        location_avg_temp.append(-1)

                else:
                    location_country_name.append(-1) 
                    location_coast_length.append(-1)
                    location_border_length.append(-1)
                    location_sea_level.append(-1)
                    location_number_of_borders.append(-1)
                    location_avg_temp.append(-1)

        for idx_Xl, lossers in enumerate(X["losser_list"]):
            if state in lossers:
                country_name.append(state)
                coast_length.append(country_df.iloc[idx]["coast_length"])
                border_length.append(country_df.iloc[idx]["border_length"])
                sea_level.append(country_df.iloc[idx]["sea_level"])
                number_of_borders.append(country_df.iloc[idx]["number_of_borders"])
                avg_temp.append(country_df.iloc[idx]["temp"])
                label.append(0)

                #Add losser location details
                res = difflib.get_close_matches(str(X.iloc[idx_Xl]["location"]), world_countries)
                if(len(res) > 0):
                    country_indexes = country_df.index[country_df["country"] == res[0]].tolist()
                    if (len(country_indexes) > 0):
                        country_index = country_indexes[0]
                        location_country_name.append(res[0]) 
                        location_coast_length.append(country_df.iloc[country_index]["coast_length"])
                        location_border_length.append(country_df.iloc[country_index]["border_length"])
                        location_sea_level.append(country_df.iloc[country_index]["sea_level"])
                        location_number_of_borders.append(country_df.iloc[country_index]["number_of_borders"])
                        location_avg_temp.append(country_df.iloc[country_index]["temp"])
                    else:
                        location_country_name.append(-1) 
                        location_coast_length.append(-1)
                        location_border_length.append(-1)
                        location_sea_level.append(-1)
                        location_number_of_borders.append(-1)
                        location_avg_temp.append(-1)
                else:
                    location_country_name.append(-1) 
                    location_coast_length.append(-1)
                    location_border_length.append(-1)
                    location_sea_level.append(-1)
                    location_number_of_borders.append(-1)
                    location_avg_temp.append(-1)

    dict = {"name": country_name, "coast_length" : coast_length,
    "border_length" : border_length, "sea_level": sea_level,
    "number_of_borders" : number_of_borders, "avg_temp" : avg_temp,
    "location_coast_length" : location_coast_length, "location_border_length" : location_border_length,
    "location_sea_level" : location_sea_level, "location_number_of_borders" : location_number_of_borders,
    "location_avg_temp":location_avg_temp, "label" : label}
    total_X = pd.DataFrame(dict)
    total_X.info()
    total_X = total_X[total_X["location_coast_length"] != -1]
    total_X.info()
    total_X.to_csv("ML-data/X_total.csv")
    return total_X

#stage 4.b Cleaning the dataset
def clean_X(X_total):
    for column in ["coast_length","border_length","sea_level","number_of_borders","avg_temp", "location_coast_length","location_border_length","location_sea_level","location_number_of_borders","location_avg_temp"]:
        removeOutliers(X_total,column)
        X_total[column] = X_total[column] /X_total[column].abs().max()
    del X_total["Unnamed: 0"]
    X_total = X_total.drop_duplicates()
    print(X_total.label.value_counts())
    label1_indexes = X_total[X_total["label"] == 1].index.tolist()
    print("hi")
    print(len(label1_indexes))
    random_rows = random.sample(label1_indexes, 688)
    X_total = X_total.drop(random_rows, axis=0)
    print(X_total.label.value_counts())
    return X_total

#stage 4.c Logistic Regression
def logistic_regression(df, feature_cols):
    #split dataset in features and target variable
    
    X = df[feature_cols] # Features
    y = df.label # Target variable

    #Train and split information
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=1,shuffle=True)

    #Creating logisticRegression
    logreg = LogisticRegression()
    #Running fit
    logreg.fit(X_train,y_train)
    #Applaying fit on test
    y_pred=logreg.predict(X_test)

    #Generating confusion_matrix
    valid_invalid_matrix = metrics.confusion_matrix(y_test, y_pred)

    class_names=[0,1] # name  of classes
    fig, ax = plt.subplots()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names)
    plt.yticks(tick_marks, class_names)
    # create heatmap
    sns.heatmap(pd.DataFrame(valid_invalid_matrix), annot=True, cmap="YlOrRd" ,fmt='g')
    ax.xaxis.set_label_position("top")
    plt.tight_layout()
    plt.title('Confusion matrix', y=1.1)
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label')

    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
    print("Precision:",metrics.precision_score(y_test, y_pred))
    print("Recall:",metrics.recall_score(y_test, y_pred))
    print(valid_invalid_matrix)
    
    logit_roc_auc = roc_auc_score(y_test, logreg.predict(X_test))
    fpr, tpr, thresholds = roc_curve(y_test, logreg.predict_proba(X_test)[:,1])
    plt.figure()
    ax = plt.gca()
    ax.set_facecolor('xkcd:sky blue')
    plt.plot(fpr, tpr, label='Logistic Regression (area = %0.2f)' % logit_roc_auc)
    plt.plot([0, 1], [0, 1],'r--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")


    plt.show()

#stage 5.a Wow effect:
def create_video(df, country_df, column, year_begin, year_end):
    max_wars = 0
    year_wars_count = [] 
    for year in range(year_begin,year_end + 1):
        wars_count = []
        new_df = df[(df["finish_year"] - year >= 0)]
        new_df = new_df[new_df["start_year"] - year <= 0]
        wars = new_df.index.tolist()
        for idx, country in enumerate(country_df["country"]):
            wars_in_country = (str(country_df.iloc[idx]["winning_wars"]).split(",")[:-1])
            wars_in_country.extend((str(country_df.iloc[idx]["lost_wars"]).split(",")[:-1]))
            sum_casualties = 0
            wars_count.append(sum([df.iloc[war]["casualties_A"] + df.iloc[war]["casualties_B"] for war in wars if str(war) in wars_in_country]))
        year_wars_count.append(wars_count)
    
    for year_wars in year_wars_count:
        this_year = max(year_wars)
        if max_wars < this_year:
            max_wars = this_year
    
    index = country_df[country_df["country"]== "Fiji"].index[0]
    for idx, year_wars in enumerate(year_wars_count):
        country_df["wars_per_year"] = year_wars
        #country_df.at[index,"wars_per_year"] = max_wars
        plot_world_video(country_df,"wars_per_year", year_begin + idx, "Reds")
                    
        

#code: 
#createDatabases() # part 1.a
#run_combine_csv() # part 1.b
#country_df = create_countries_dataframe() # part 1.c
country_df = pd.read_csv("country_df.csv")
df = pd.read_csv("DataFrames.csv")

#clean_country(country_df)
#country_df.sort_values(by="coast_length") 
#country_df = country_df.drop_duplicates(subset="country")
#country_df.sort_values(by="country")
# df = pd.read_csv("Databases/combine_files.csv")
# intial_cleanup(df) # part 2.a
# special_treatment_for_years(df) # part 2.b
# build_up(df) # part 2.c
# normalize(df)# part 2.d
# df = population(df)# part 2.e
# population_ratio(df)# part 2.f
# replace_countries_name(df, "winner_list") # part 2.g
# replace_countries_name(df, "losser_list") # part 2.g
# replace_countries_name(df, "location") # part 2.g
#build_up_for_countries(df,country_df) # part 2.h
#country_df.to_csv("Gcountry_df.csv")
#plot_world_sum(country_df[["country", "rate"]], "rate","Spectral")
#build_up_for_countries(df,country_df)
#plot_world(country_df,"battles_in_country","jet")
#MultiGraph(country_df,["sea_level","coast_length","border_length","wars_victory"])
#MultiGraph(country_df[(country_df["country"]!="Canada") & ((country_df["country"]!="United States of America"))],["coast_length","total_wars_participate","wars_victory"])
#plot_world(country_df,"deimperialism_wars","ocean")
#df["sum_of_deaths"] = df.apply(lambda row: float(row.casualties_B) + float(row.casualties_A), axis = 1)
#plot_world_special_treatment(df[["location", "sum_of_deaths"]], "location", "sum_of_deaths")

#df["sum_of_army"] = df.apply(lambda row: float(row.strength_A) + float(row.strength_B), axis = 1)
#plot_world_special_treatment(df[["losser_list", "sum_of_army"]], "losser_list", "sum_of_army")
# plot_world(country_df,"coast_length","cividis")
#plot_world_special_treatment(df[["location", "sum_of_deaths"]], "location", "sum_of_deaths")
#df.to_csv('DataFrame.csv')
#plt.show()
#X_total = build_X_total(country_df)
X_total = pd.read_csv("ML-data/X_total.csv")
#print(df.terror.value_counts())
create_video(df, country_df,"battles_in_country",1918,2018)
#X_total = clean_X(X_total)
#logistic_regression(X_total,["coast_length","border_length","sea_level","number_of_borders","avg_temp", "location_coast_length","location_border_length","location_sea_level","location_number_of_borders","location_avg_temp"])
