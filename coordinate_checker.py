#uses various checks to confirm that the obtained coordinates are within acceptable margin of error.

import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *
import arcpy
import random
import re

# Requires API key
gmaps = googlemaps.Client(key='AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0')


arcpy.env.overwriteOutput = True


def get_shp_from_coordinates(points):
    sr_g = arcpy.SpatialReference(4326)
    m = "C:/gis/tempo.shp"
    point = arcpy.Point()
    pointGeometryList = []
    for pt in points:
        point.X = pt[0]
        point.Y = pt[1]
        pointGeometry = arcpy.PointGeometry(point).projectAs(sr_g)
        pointGeometryList.append(pointGeometry)
    # arcpy.CopyFeatures_management(pointGeometryList, m)
    arcpy.Delete_management(m)
    arcpy.CopyFeatures_management(pointGeometryList, m)
    arcpy.AddField_management(m, "X", "DOUBLE")
    arcpy.AddField_management(m, "Y", "DOUBLE")
    with arcpy.da.UpdateCursor(m, ["OID@", "X", "Y"]) as cursor:
        for row in cursor:
            row[1] = points[row[0]][0]
            row[2] = points[row[0]][1]
            cursor.updateRow(row)
    return m




def get_coordinates_to_Abbr_dict(shp):
    m = "C:/gis/pushpushaa.shp"
    # if its completely inside, do one thing, if its completely outside, do other.
    boundary_features = "./../agri project/shp/tl_2017_us_states.shp"
    # overwrite table
    arcpy.SpatialJoin_analysis(shp, boundary_features, m, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN")
    _dict_ = {str((f[2], f[1])): f[0] for f in arcpy.da.SearchCursor(m, ['Abbr', "X", "Y"], "")}
    return _dict_


def get_coordinates_to_link_dict(shp):
    m = "C:/gis/pushpushaad.shp"
    # if its completely inside, do one thing, if its completely outside, do other.
    link_features = "./../agri project/railnet/gis/railway_ln2016.shp"
    # overwrite table
    arcpy.SpatialJoin_analysis(shp, link_features, m, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "WITHIN_A_DISTANCE", "20 Miles")
    _dict_ = {str((f[2], f[1])): f[0] for f in arcpy.da.SearchCursor(m, ['WayId', "X", "Y"], "")}
    return _dict_




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
        print ("NOT FOUND: PLEASE ADD {0} to place_to_coord_.csv".format(a))
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
name_to_coord1 = name_to_coord.dropna().transpose().to_dict()
name_to_coord2 = {x: [(float(y['0'][1:-1].split(',')[0]), float(y['0'][1:-1].split(',')[1])), y['1']] for x, y in
                  name_to_coord1.iteritems()}
place_coordi_dict = name_to_coord2
place_coordi_dict[""] = [(0,0), 0]




#check if the coordinate is in the state


list_all_coords = [x[0] for x in place_coordi_dict.values()]
list_all_coords = [(y,x) for (x,y) in list_all_coords]

shp = get_shp_from_coordinates(list_all_coords)
coordinates_to_Abbr = get_coordinates_to_Abbr_dict(shp)
coordinates_to_Abbr['(0, 0)'] = " "


place_coordi_dict1 = {x:coordinates_to_Abbr[str(y[0])] for x,y in place_coordi_dict.iteritems()}

#
# aaa = random.sample(place_coordi_dict, 5)
# sss = {x:place_coordi_dict[x] for x in aaa}
# place_coordi_dict1 = {x:coordinates_to_Abbr[str(y[0])] for x,y in sss.iteritems()}

for key, value in place_coordi_dict1.iteritems():
    try:
        found[key] = [value.upper(), re.search(r',[ ]*([A-Za-z][A-Za-z])', key).group(1).upper()]
    except:
        print key


found = {x:y for x,y in found.iteritems() if y[0] !=y[1]}
found = {x:y for x,y in found.iteritems() if y[0] !=" "}

pd.DataFrame(found).transpose().to_csv("./intermediate/ods_in_other_states.csv")
print ("Look 'ids_in_other_states.csv' in the intermediate folder")

#check if the coordinate is close to our network


list_all_coords = [x[0] for x in place_coordi_dict.values()]
list_all_coords = [(y,x) for (x,y) in list_all_coords]

shp = get_shp_from_coordinates(list_all_coords)
coordinates_to_link = get_coordinates_to_link_dict(shp)
coordinates_to_link['(0, 0)'] = " "


place_coordi_dict1 = {x:str(coordinates_to_link[str(y[0])]) for x,y in place_coordi_dict.iteritems()}



# aaa = random.sample(place_coordi_dict1, 5)
# sss = {x:place_coordi_dict1[x] for x in aaa}
#
# #place_coordi_dict1 = {x:coordinates_to_link[x] for x,y in sss.iteritems()}

found = {}
for key, value in place_coordi_dict1.iteritems():
    try:
        found[key] = [value, re.search(r'[0-9]+', str(value)).group(0)]
    except Exception as e:
        print key



found = {x:y for x,y in found.iteritems() if y[0] !=y[1]}
found = {x:y for x,y in found.iteritems() if y[0] !=" "}

print ("The list of address that are more than 20 miles more than any railroad")
print found




