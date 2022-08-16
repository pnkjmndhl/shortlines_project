import pandas as pd

start_coord = "o_coord"
end_coord = "t_coord"

# final table columns
no_of_cars = "nos"
wt_per_car = "wtpcr"
commodity = "cmdty"
online_dist = "dist"

all_dist = "dist1"
start_rr = "rr1"
current_rr = "rr"
forwarded_rr = "rr2"
origin = 'origin'
destination = 'destination'
transfer_1 = "o1"
transfer_2 = "d1"
total_wt = 'wt'
inout = 'inout'
commodity_new = 'commo_new'
use_rate = "use_rate"


shortline_dist = "_d_"
google_maps_dist = "distance"
unique_ods = "od"



#calculating inorout
inout_dict = {
    "In": 'Terminating',
    "Out": "Originating",
    "Bridge" : 'Local',
    'Empty': 'Local',
    'Local': 'Local',
    "LOCAL": "Local",
    'Received': 'Terminating',
    'Operating': 'Local',
    'ORIGINATING': 'Originating',
    "TERMINATING": "Terminating",
    "Forwarded": 'Originating',
    '': 'Local',
    'Inbound': 'Terminating',
    'Outbound': "Originating",
    'ORIGINATE': 'Originating',
    'TERMINATE': 'Terminating',
    'Local': 'Local'
    }


od_dist_time_csv ="./intermediate/od_dist_time.csv"
name_to_coord_csv = "./intermediate/name_to_coord.csv"


summary1_csv = "./intermediate/summary1.csv"
summary2_csv = "./intermediate/summary2.csv"
summary3_csv = "./intermediate/summary3.csv"




# constants

truck_speed = [45, 45, 45, 45]  # mph
rail_speed = 20  # mph
base = 0
compare = [1, 2, 3]
min_cost_pcar = 325

base_indexes = [8, 4, 0]
s1_indexes = [9, 5, 1]
s2_indexes = [10, 6, 2]
s3_indexes = [11, 7, 3]

type_conversion_dict = {"Dry van": 0, "Hopper": 1, "Tanker": 2, "Dry Van": 0, "Tanker ": 2}

rail_rate_df = pd.read_csv("input/RATES.csv").loc[:, 'SCTG':'RTM']
truck_rate_df = pd.ExcelFile("input/Rate Table per ton.xlsx").parse("Sheet1")
truck_rate_df.drop(['Truck Configuration'], inplace=True, axis=1)

commodty_distr_df = pd.ExcelFile("input/Trailer type.xlsx").parse("Sheet1")
commodty_distr_df.drop(['Description'], inplace=True, axis=1)

# truck_rate_df = truck_rate_df.transpose().reset_index()

# select the columns from start to end
model1_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("Shpmt Freight Rate Models").loc[0:37, 'SCTG':'Group']
model2_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("22-Mkt Share Frt-Trans time").loc[0:3,
            'SCTG':'Group']

cmdty_list = ['"{:02}"'.format(int(x)) for x in list(model1_df['SCTG'].unique()) if str(x) != 'nan']