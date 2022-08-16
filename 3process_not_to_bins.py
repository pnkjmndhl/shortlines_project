import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *

# Requires API key
gmaps = googlemaps.Client(key='AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0')



def get_distance_time(o, d):
    if ((o == 0 or d == 0)):
        return (np.nan, np.nan)
    if ((o == (0, 0)) or (d == (0, 0))):
        return (np.nan, np.nan)
    if (o, d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o, d)]
    print "New Coordinate Found"
    print("{0}->{1}".format(o, d))
    result = gmaps.distance_matrix(o, d)
    time = result['rows'][0]['elements'][0]['duration']['text']
    dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",", "")) / 1.6
    od_dist_time_dict[(o, d)] = time, dist
    return (time, dist)


# functions
def get_dist_bin(val):
    diff_list = [abs(x - val) for x in distance_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = distance_bins.keys()[min_val_index]
    return bin


def use_rate_bin(val):
    diff_list = [abs(x - val) for x in use_rate_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = use_rate_bins.keys()[min_val_index]
    return bin


def get_od(dist):
    if dist in unique_distances.keys():
        return unique_distances[dist]
    else:
        maxi_mum = max(unique_distances.values())
        unique_distances[dist] = maxi_mum + 1
        return maxi_mum + 1


def get_coordinate(a):
    # print "{0}->{1}".format(a,b)
    global place_coordi_dict
    if a == "":
        return 0
    if a in place_coordi_dict.keys():
        return place_coordi_dict[a][0]
    else:
        print ("NOT FOUND: PLEASE ADD {0} to place_to_coord.csv".format(a))
        # try: #this did not add proper coordinates (so removed, it would be done manually now)
        #     location = geolocator.geocode(a)[1]
        # except:
        #     print ("NOT FOUND: {0}".format(a))
        #     place_coordi_dict[a] = [-99, "error"]
        #     return 0
        # place_coordi_dict[a] = [location, "auto4"]
        place_coordi_dict[a] = [(0,0), "error"]
        return (0,0)


unique_od_ids = {1: 1000}

def get_unique_od_ids(a, b):
    # print "{0}->{1}".format(a,b)
    if (a, b) in unique_od_ids.keys():
        return unique_od_ids[(a, b)]
    else:
        value = max(unique_od_ids.values()) + 1
        unique_od_ids[(a, b)] = value
        # unique_od_ids[(b, a)] = value #origin to destination is different to destination to origin use rate
        return value


# def get_od_dist_time_dict(filename):
#     dumm = pd.DataFrame.from_csv(filename).reset_index()
#     dumm['new'] = "(" + dumm['index'] + "," + dumm['Unnamed: 1'] + ")"
#     dumm.drop(['index', 'Unnamed: 1'], axis=1, inplace=True)
#     dumm = dumm.set_index("new")
#     dumm1 = dumm.transpose().to_dict()
#     dumm2 = {eval(x): [y['0'], y['1']] for x, y in dumm1.iteritems()}
#     return dumm2


# read the output file (from combined)
data = pd.read_csv("input/shortline_output_all.csv")
data.drop("cmdty", axis=1, inplace=True)
data.rename(columns={"commo_new": "cmdty"}, inplace=True)

# to get the use rate
unique_distances = {1: 1}

# retrieve
#od_dist_time_dict = get_od_dist_time_dict(od_dist_time_csv)
od_dist_time_dict = np.load('./intermediate/od_dist_time_dict.npy').item()


name_to_coord = pd.DataFrame.from_csv(name_to_coord_csv)[['0', '1']]
name_to_coord['0'] = name_to_coord['0'].replace("0", '(0,0)')
name_to_coord1 = name_to_coord.dropna().transpose().to_dict()
name_to_coord2 = {x: [(float(y['0'][1:-1].split(',')[0]), float(y['0'][1:-1].split(',')[1])), y['1']] for x, y in
                  name_to_coord1.iteritems()}
place_coordi_dict = name_to_coord2
place_coordi_dict[""] = [0, 0]

#pd.DataFrame.from_dict(place_coordi_dict).transpose().to_csv('ball.csv')
#drop if the coordinates origin or destination is nan

#data.to_csv("apple.csv")

# search on google maps

#geolocator = Nominatim(user_agent="rail_project_pdahal1")
data[start_coord] = data['origin'].map(get_coordinate)
data[end_coord] = data['destination'].map(get_coordinate)


data[google_maps_dist] = data.apply(lambda x: get_distance_time(x[start_coord], x[end_coord])[1], axis=1)
np.save('./intermediate/od_dist_time_dict', np.array(dict(od_dist_time_dict)))

# for each unique value of origin and destination (reversed), give a distance called od
data['od'] = data.apply(lambda x: get_unique_od_ids(x['origin'], b=x['destination']), axis=1)

#pd.DataFrame(place_coordi_dict).transpose().to_csv(name_to_coord_csv)

#if distance unknown then use the distance provided
data[google_maps_dist] = np.where((pd.isnull(data[google_maps_dist])) & (data[all_dist] >0), data[all_dist], data[google_maps_dist])
data[google_maps_dist] = np.where((pd.isnull(data[google_maps_dist])) & (data[inout] == "Local") & (data[shortline_dist] > 0), data[shortline_dist], data[google_maps_dist])

data.drop(['Unnamed: 0'], axis=1, inplace=True)
#
data[data[[commodity, google_maps_dist]].isnull().any(axis=1)].to_csv("./intermediate/discarded_records.csv")


data.dropna(subset=[total_wt, unique_ods, commodity, no_of_cars, google_maps_dist], inplace=True)



# data1 = data[[pd.isnull(data[commodity])]]
#
# #data1 = data1[[pd.isnull(data1[total_wt])]]

data = data.fillna("Null")

data.to_csv("input/shortlines_output_all_extended.csv")


data0 = pd.pivot_table(data, values=[total_wt, no_of_cars], index=[commodity, current_rr, shortline_dist, transfer_1, transfer_2, start_coord, end_coord, google_maps_dist],
                       aggfunc={total_wt: np.sum, no_of_cars: np.sum}).reset_index()


data0.to_csv("input/shortlines_output_all_unique_ods.csv")

data1 = data0.copy()

# data = data.rename(columns={commodity: "commodty"}).reset_index()
#data0 = data0[[total_wt, commodity, google_maps_dist, shortline_dist, no_of_cars, current_rr, transfer_1, transfer_2, start_coord, end_coord]]

# summaries
summary = pd.pivot_table(data0, values=[total_wt], index=[current_rr], aggfunc={total_wt: np.sum}).reset_index()
summary.to_csv(summary1_csv)

# rr vs total wt by commodity
summary2 = pd.pivot_table(data0, values=[total_wt], index=[current_rr, commodity],
                          aggfunc={total_wt: np.sum}).reset_index()
summary2.to_csv(summary2_csv)

summary3 = pd.pivot_table(data0, values=[total_wt, no_of_cars], index=[current_rr, commodity],
                          aggfunc={total_wt: np.sum, no_of_cars: np.sum}).reset_index()
summary3.to_csv(summary3_csv)

#
# # calculating use rate
#
data0 = data0.rename(columns={total_wt: use_rate})
data0 = data0[[commodity, google_maps_dist, shortline_dist, current_rr, no_of_cars, use_rate, start_coord, end_coord, transfer_1, transfer_2]]
# use_rate_df['use_rate_bin'] = use_rate_df['use_rate'].map(use_rate_bin)
data0.to_csv('./intermediate/pred1.csv')
#
#
# data1 = data1.rename(columns={total_wt: use_rate})
# data1 = data1[[commodity, current_rr, transfer_1, transfer_2, start_coord, end_coord, google_maps_dist, no_of_cars, use_rate, shortline_dist]]
# # use_rate_df['use_rate_bin'] = use_rate_df['use_rate'].map(use_rate_bin)
# data1[(data1.rr == "AGR") | (data1.rr == "BPRR")].to_csv('./intermediate/pred2.csv')








