import pandas as pd
import numpy as np
import math
import os
from variables import *


# functions
def get_dist_bin(val):
    db1 = {(val - x):y for x,y in distance_bins.iteritems()}
    db2 = [x for x in db1.keys() if x > 0]
    return db1[min(db2)]


def use_rate_bin(val):
    urb1 = {(val - x):y for x,y in use_rate_bins.iteritems()}
    urb2 = [x for x in urb1.keys() if x > 0]
    return urb1[min(urb2)]


def get_od(dist):
    if dist in unique_distances.keys():
        return unique_distances[dist]
    else:
        maxi_mum = max(unique_distances.values())
        unique_distances[dist] = maxi_mum + 1
        return maxi_mum + 1


def get_coordinate(a):
    # print "{0}->{1}".format(a,b)
    if a in place_coordi_dict.keys():
        return place_coordi_dict[a]
    else:
        return 0


unique_od_ids = {1: 1000}


def get_unique_od_ids(a, b):
    # print "{0}->{1}".format(a,b)
    if (a, b) in unique_od_ids.keys():
        return unique_od_ids[(a, b)]
    else:
        value = max(unique_od_ids.values()) + 1
        unique_od_ids[(a, b)] = value
        #unique_od_ids[(b, a)] = value #origin to destination is different to destination to origin use rate
        return value


#use the lower bins
distance_bins = {0: 50, 100: 200, 300: 400, 500: 600, 700: 800, 900:1000, 1100: 1200}
use_rate_bins = {0:100, 200: 250, 300:500, 700: 750, 800: 1000, 1200: 1500, 1800:2000, 2200:2500, 2800:3750, 4700:5000, 5300:7500, 9700:10000, 10300:25000, 39700:50000, 60300:100000, 139700:250000, 375000:375000}
# use_rate_bins = {1000:1, 5000:2}


#to get the use rate
unique_distances = {1: 1}


filenames = ["mode_split_pred1_0_1","mode_split_pred1_0_2","mode_split_pred1_0_3"]

for filename in filenames:
    data = pd.read_csv("./output/" + filename + ".csv")
    #all_commodities = list(data.commodty.unique())
    data['dist_bin'] = data[google_maps_dist].map(get_dist_bin)
    #work on this later
    keep_columns = ['Unnamed: 0', commodity, google_maps_dist, use_rate, 'dist_bin', 'lost_rev', 'lost_ton']
    data = data[keep_columns]
    #calculating use rate

    use_rate_df = pd.pivot_table(data, values=['use_rate', 'lost_rev', 'lost_ton'], index=[commodity, 'dist_bin', 'Unnamed: 0'], aggfunc={use_rate:np.sum, 'lost_rev':np.sum, 'lost_ton':np.sum, }).reset_index()
    #use_rate_df = use_rate_df.rename(columns={'wt': 'use_rate'})
    use_rate_df['use_rate_bin'] = use_rate_df[use_rate].map(use_rate_bin)
    use_rate_df1 = pd.pivot_table(use_rate_df, values=[use_rate, 'lost_rev', 'lost_ton'], index=[commodity, 'dist_bin', 'use_rate_bin'], aggfunc={use_rate:np.sum, 'lost_rev':np.sum, 'lost_ton':np.sum}).reset_index()
    use_rate_df1['percent'] = use_rate_df1['use_rate']/use_rate_df1.use_rate.sum()
    use_rate_df1.to_csv( "./output/" + filename + "_binned.csv")

