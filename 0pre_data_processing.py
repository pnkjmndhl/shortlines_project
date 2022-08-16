import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *

# Requires API key
gmaps = googlemaps.Client(key='AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0')


def get_distance_time(o, d):
    try:
        if (pd.isnull(o) or pd.isnull(d)):
            return (np.nan, np.nan)
    except:
        pass
    if ((o == 0 or d == 0)):
        return (np.nan, np.nan)
    if ((o == (0, 0)) or (d == (0, 0))):
        return (np.nan, np.nan)
    if (o, d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o, d)]
    print "New Coordinate Found"
    print("{0}->{1}".format(o, d))
    result = gmaps.distance_matrix(o, d)
    try:
        time = result['rows'][0]['elements'][0]['duration']['text']
        dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",", "")) / 1.6
        od_dist_time_dict[(o, d)] = time, dist
        return [time, dist]
    except:
        print "Error: "
        return [0,0]


def get_bool_null(o):
    o = str(o)
    if o== 'nan':
        return 1
    elif ((o == '(0,0)') or (o == '(0, 0)') or (o == '(0.0, 0.0)') ):
        return 1
    else:
        #print type(o)
        #print o
        return 0



def get_dist(o,o1,d1,d):
    if (get_bool_null(o1)==1) and (get_bool_null(d1)!=1):
        return get_distance_time(eval(str(o)),eval(str(d1)))[1]
    elif (get_bool_null(d1)==1) and (get_bool_null(o1) !=1):
        return get_distance_time(eval(str(o1)), eval(str(d)))[1]
    else:
        return get_distance_time(eval(str(o1)), eval(str(d1)))[1]







od_dist_time_dict = np.load('./intermediate/od_dist_time_dict.npy').item()


name_to_coord = pd.DataFrame.from_csv(name_to_coord_csv)[['0', '1']]
name_to_coord['0'] = name_to_coord['0'].replace("0", '(0,0)')
name_to_coord1 = name_to_coord.dropna().transpose().to_dict()
name_to_coord2 = {x: [(float(y['0'][1:-1].split(',')[0]), float(y['0'][1:-1].split(',')[1])), y['1']] for x, y in
                  name_to_coord1.iteritems()}
place_coordi_dict = name_to_coord2
place_coordi_dict[""] = [0, 0]
place_coordi_dict = {x:y[0] for x,y in place_coordi_dict.iteritems()}




WSOR = pd.ExcelFile('./input/CARRIER_DATA2/WSOR Study Data(mod).xlsx').parse("Data")

WSOR['o1_'] = WSOR['Online origin'].map(place_coordi_dict)
WSOR['d1_'] = WSOR['online destination'].map(place_coordi_dict)


WSOR['g_dist'] = WSOR[['o1_', 'd1_']].apply(lambda x: get_distance_time(x.o1_, x.d1_)[1], axis = 1)
WSOR['Online miles'] = np.where(pd.isnull(WSOR['Online miles']),WSOR['g_dist'], WSOR['Online miles'])



WSOR = WSOR[['Description', 'Total Cars', 'Traffic Type', 'Commodity', 'Origin', 'Destination', 'O-Rd', 'D-Rd', 'Road & Junctions', 'Tons', 'Miles', 'IB/OB', 'Online miles', 'Seasonality', 'Online origin', 'online destination', 'o1_', 'd1_']]

WSOR.rename(columns = {'Online miles': 'MilesonRR'}, inplace=True)



#remove values whose total_cars ==-1 or null
index1 = WSOR['Total Cars'].index[WSOR['Total Cars'].apply(np.isnan)]
index2 = WSOR[(WSOR['Total Cars'] == -1)].index

index = list(set(list(index1) + list(index2)))
index_1 = [x-1 for x in index]

index_all = list(set(list(index) + list(index_1)))
index_2 = list(WSOR[(WSOR['Total Cars'] == -2)].index)
index_all.extend(index_2)


wsor = WSOR.drop(WSOR.index[index_all])

wsor.to_csv("./input/CARRIER_DATA2/WSOR_.csv")


np.save('./intermediate/od_dist_time_dict', np.array(dict(od_dist_time_dict)))


df = pd.ExcelFile("./input/CARRIER_DATA2/AGR and BPRR data(11-16 MOD).xlsx").parse("Sheet1")

df['o1'] = df['City Trip Start'].astype(str) + ", " + df['State Trip Start'].astype(str)
df['d1'] = df['City Trip End'].astype(str) + ", " + df['State Trip End'].astype(str)

df['o1_'] = df['o1'].map(place_coordi_dict)
df['d1_'] = df['d1'].map(place_coordi_dict)

df['g_dist'] = df[['o1_', 'd1_']].apply(lambda x: get_distance_time(x.o1_, x.d1_)[1], axis = 1)

df.drop(["Average GWI Miles"], inplace= True, axis = 1)

df.to_csv("./input/CARRIER_DATA2/AGR_BPRR_.csv")


np.save('./intermediate/od_dist_time_dict', np.array(dict(od_dist_time_dict)))





