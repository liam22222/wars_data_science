from numpy import nan
import pandas as pd
import geopandas
import matplotlib.pyplot as plt



world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
world = world[(world.pop_est>0) & (world.name!="Antarctica")]

def plot_world_video(df, column, year, cmapR="rainbow"):
    df_new = df.rename(columns={'country': 'name'}, copy=True)
    combined = world.merge(df_new,on="name")
    combined.append(pd.Series(), ignore_index=True)
    graph = combined.plot(column=column , legend=True, cmap=cmapR,
    legend_kwds={"label" : "{0} Number of wars".format(year), "orientation" : "horizontal"})
    graph.set_facecolor('#00699460')
    plt.savefig('videos/history/{0}.png'.format(year))
    #plt.show()
    

def plot_world(df, column, cmapR="rainbow"):
    df_new = df.rename(columns={'country': 'name'}, copy=True)
    combined = world.merge(df_new,on="name")
    graph = combined.plot(column=column ,legend=True, cmap=cmapR,
     legend_kwds={"label" : "Coast length (Kilometers)", "orientation" : "horizontal"})
    graph.set_facecolor('#00699460')
    plt.show()

def plot_world_sum(df, column, cmapR="rainbow"):
    df_new = df.rename(columns={'country': 'name'}, copy=True)
    for idx, state in enumerate(df_new["name"]):
        if df_new.iloc[idx][column] == nan:
            #This country has none wars in this column
            df_new.iloc[idx][column] = 0
        else:
            #This country have wars on this column, removing the last part which indecate nothing
            df_new.iloc[idx][column] = float(len(str(df_new.iloc[idx][column]).split(',')) - 1)
    df_new[column] = pd.to_numeric(df_new[column],errors='coerce')
    combined = world.merge(df_new,on="name")
    graph = combined.plot(column=column ,legend=True, cmap=cmapR, 
    legend_kwds={"label" : "Precentage of winning wars (%)", "orientation" : "horizontal"})
    graph.set_facecolor('#00699460')
    plt.show()
    

def plot_world_special_treatment(df, column_state, column_info):
    country_sum = []
    for idx, state in enumerate(world.name):
        wars_with_country = df[column_state].str.contains(state)
        country_sum.append(sum(df.loc[wars_with_country,column_info]))

    world["total_death"] = country_sum
    world.plot(column="total_death",cmap="RdBu_r", legend=True,
     legend_kwds={"label" : "Death by location", "orientation" : "horizontal"})

    plt.show()
