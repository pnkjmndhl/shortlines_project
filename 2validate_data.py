#calculate possible missing values
import pandas as pd
from variables import *
import numpy as np
import math

all = pd.read_csv("intermediate/shortlines_output_raw.csv")


def get_commo(value):
    if pd.isnull(value):
        return np.nan
    value4 = '"' + value[0:4] + '"'
    value5 = '"' + value[0:5] + '"'
    value = '"' + value + '"'
    if value5 in stcg_dict:  # check if its in 5 letters, thats more accurate
        dumm = stcg_dict[value5]
        found_dict[value] = dumm
        return dumm
    elif value4 in stcg_dict:
        dumm = stcg_dict[value4]
        found_dict[value] = dumm
        return dumm
    elif value in stcg_49_dict:
            dumm = stcg_49_dict[value]
            found_dict[value] = dumm
            return dumm
    else:
        not_found_dict[value] = [value4, value5]


def get_wt_p_car(comm, rr, wtpcr):
    if ((math.isnan(wtpcr)) and (not pd.isnull(comm))): # the value of commodity should be available
        a = float(wtpcr_df[(wtpcr_df[commodity_new] == comm) & (wtpcr_df[current_rr] == rr)][wt_per_car])
        return a
    else:
        return wtpcr



def get_standardardized_commo(value):
    value = str(value)
    try:
        value = value.strip()
        value = str(value)
    except:
        pass
    try:
        a = int(value)
    except:
        value = live_dict[value.strip().upper()][1]
        if (value == 0) or (value == "NAN") or (pd.isnull(value)):
            return np.nan
    if value[0] == '"':  # removing apostrophies
        value = value[1:-1]
    if len(value) == 6:  # if 6 digits then add 0 in front
        value = '0' + value
    return value


print ("getting SCTG, calculating possible fix for missing values..")

all.inout = all.inout.map(inout_dict)

all = all.reset_index()



conv_df = pd.read_csv("./input/conversion.csv")
STCG_df1 = pd.ExcelFile("./input/SCTG.xlsx").parse("STCC 4-digit").append(
    pd.ExcelFile("./input/SCTG.xlsx").parse("STCC 5-digit")).reset_index()[['STCC', 'SCTG']]
STCG_49 = pd.ExcelFile("./input/49.xlsx").parse("Sheet1").reset_index()[['STCC', 'SCTG']]

stcg_dict = STCG_df1.transpose().to_dict()
stcg_dict = {y['STCC']: y['SCTG'] for x, y in stcg_dict.iteritems()}

stcg_49_dict = STCG_49.transpose().to_dict()
stcg_49_dict = {y['STCC']: y['SCTG'] for x, y in stcg_49_dict.iteritems()}

live_dict = {}
for i in range(len(conv_df)):
    live_dict[conv_df['Unnamed: 0'][i].strip().upper()] = [conv_df['0'][i], conv_df['1'][i]]

live_dict["NAN"] = [0, 0]

all.cmdty = all.cmdty.map(get_standardardized_commo)

not_found_dict = {}
found_dict = {}
all[commodity_new] = ''

all[commodity_new] = all[commodity].map(get_commo)

print "Commodities not found in conversion.csv: {0}".format(not_found_dict)



# verified from output that all of these values are ok
# get the averages of the unknown values
all.loc[np.isnan(all[total_wt]), total_wt] = all[no_of_cars] * all[wt_per_car]  # important np.nan !=np.nan
all.loc[np.isnan(all[wt_per_car]), wt_per_car] = all[total_wt] / all[no_of_cars]  # important np.nan !=np.nan

wtpcr_df = pd.pivot_table(all, values=wt_per_car, index=[current_rr, commodity_new], aggfunc=np.mean).reset_index()
all.wt_per_car = all.apply(lambda x: get_wt_p_car(x[commodity_new], x[current_rr], x[wt_per_car]), axis=1)
all.loc[np.isnan(all[total_wt]), total_wt] = all[no_of_cars] * all[wt_per_car]  # important np.nan !=np.nan

all = all[all[total_wt] > 0]

all = all.reset_index()


colnames = [commodity,transfer_2, destination,shortline_dist , all_dist , inout, no_of_cars,transfer_1,
            origin, current_rr, start_rr, forwarded_rr, total_wt,wt_per_car , commodity_new]



all = all[colnames]

all.to_csv('./input/shortline_output_all.csv')
