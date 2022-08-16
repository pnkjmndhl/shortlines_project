import pandas as pd
import re
import numpy as np
import math
from variables import *

import sys

reload(sys)
sys.setdefaultencoding('utf8')

# extract from excel files
ACWR = pd.ExcelFile("./input/CARRIER_DATA2/ACWR.xlsx").parse("Sheet1")
AGR_BPRR = pd.read_csv("./input/CARRIER_DATA2/AGR_BPRR_.csv")
#FMRC = pd.ExcelFile("./input/CARRIER_DATA2/FMRC.xlsx").parse("Sheet1")
GNBC = pd.ExcelFile("./input/CARRIER_DATA2/GNBC.xlsx").parse("Sheet1")
INRR = pd.ExcelFile("./input/CARRIER_DATA2/INRR.xlsx").parse("Sheet1")
KYLE = pd.ExcelFile("./input/CARRIER_DATA2/KYLE_RAW2.xlsx").parse("Sheet1")
SJVR = pd.ExcelFile("./input/CARRIER_DATA2/SJVR.xlsx").parse("Sheet1")
WSOR = pd.read_csv("./input/CARRIER_DATA2/WSOR_.csv")
YSVR = pd.ExcelFile("./input/CARRIER_DATA2/YSVR.xlsx").parse("Sheet1")


#get the rr1 and rr2 for YSVR
def get_rr1_rr2(listofrr):
    # list of rr has the string of RRS separated by , (ranges from one railroad to 5)
    # the remaining would only have spaces
    rrs = listofrr.split(",")
    rrs = [x for x in rrs if not re.match(r'[    ]', x)]
    try:
        index_of_rr = rrs.index('YSVR')
    except:
        print("YSVR, not found in '{0}'. rr1 and rr2 are unknown".format(listofrr))# checked that origin is Dore, ND, rr2 always equals BNSF
        index_of_rr = -99
    if index_of_rr == 0:
        rr2 = rrs[1]
        rr1 = np.nan
    elif index_of_rr == len(rrs) - 1:
        rr1 = rrs[0]
        rr2 = np.nan
    elif index_of_rr == -99:
        rr1 = np.nan
        rr2 = rrs[0]
    else:
        rr1 = rrs[0]
        rr2 = rrs[index_of_rr + 1]
    return [rr1, rr2]


def get_inout(val):
    if val == 'DORE , ND':
        return 'Outbound'
    else:
        return 'Inbound'


# preparing acwr data ??? Interline Off-Line O/D
acwr = ACWR[['Sum of Num Of Cars', 'Median Weight', 'In Out', 'Commodity', 'Median Mileage from Station to Interchange',
             'Chrg Patron Id', 'Chrg Rule 260 Cd', 'Onl Patron Station Name', 'Interline Off-Line O/D']]

acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace({'ABRDN': "Aberdeen, NC"})
acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace({'NORWO': "Norwood, NC"})
acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace({'CHLTE': "Charlotte, NC"})

acwr['Onl Patron Station Name'] = acwr['Onl Patron Station Name'] + ", NC"

acwr['origin'] = ''
acwr['dest'] = ''


for i in range(len(acwr)):
    if acwr['In Out'].iloc[i] == 'In':
        acwr.at[i, 'rr1'] = acwr['Chrg Patron Id'].iloc[i]
        acwr.at[i, 'o1'] = acwr['Chrg Rule 260 Cd'].iloc[i]
        acwr.at[i, 'origin'] = acwr['Interline Off-Line O/D'].iloc[i]
        acwr.at[i, 'dest'] = acwr['Onl Patron Station Name'].iloc[i]
    elif acwr['In Out'].iloc[i] == 'Out':
        acwr.at[i, 'rr2'] = acwr['Chrg Patron Id'].iloc[i]
        acwr.at[i, 'd1'] = acwr['Chrg Rule 260 Cd'].iloc[i]
        acwr.at[i, 'origin'] = acwr['Onl Patron Station Name'].iloc[i]
        acwr.at[i, 'dest'] = acwr['Interline Off-Line O/D'].iloc[i]
    else:
        acwr.at[i, 'origin'] = np.nan
        acwr.at[i, 'dest'] = np.nan
        acwr.at[i, 'rr1'] = np.nan
        acwr.at[i, 'o1'] = np.nan
        acwr.at[i, 'rr2'] = np.nan
        acwr.at[i, 'd1'] = np.nan

acwr['dest'] = acwr['dest'].replace('Outbound Destinations Unknown', np.nan)
acwr = acwr.drop(['Chrg Patron Id', 'Chrg Rule 260 Cd', 'Interline Off-Line O/D', 'Onl Patron Station Name'],axis=1)
acwr['rr'] = 'acwr'
acwr = acwr.rename(columns={'Sum of Num Of Cars': no_of_cars, 'Median Weight': wt_per_car, 'Commodity': commodity,
                            'Median Mileage from Station to Interchange': shortline_dist, 'rr1': start_rr,
                            'rr': current_rr, 'rr2': forwarded_rr, 'In Out': inout,
                            'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

# done
def calculate_bprr_od(type, o1, d1, o, d):
    # return o, o1, d1, d
    if type == "Forwarded":
        return o1, np.nan, d1, d
    elif type == "Received":
        return o, o1, np.nan, d1
    else:
        return o, o1, d1, d



# preparing AGR_BPRR data
agr = AGR_BPRR
agr = agr[['2017Total Cars', 'Average Net Weight', 'STCC Description', 'Interchange Road From', 'City Trip Start',
           'State Trip Start', 'City Trip End', 'State Trip End', 'Traffic Type',
           'Interchange Road To', 'Average TMS Miles', 'WB Origin', 'WB Destination', 'Railroad Id', 'g_dist']]
agr = agr.replace(',   ', np.nan)
agr = agr.replace('Missing', np.nan)
agr = agr.replace('N/A', np.nan)

agr['start'] = agr['City Trip Start'] + ", " + agr['State Trip Start']
agr['end'] = agr['City Trip End'] + ", " + agr['State Trip End']


agr['o'], agr['o1'], agr['d1'], agr['d'] = zip(*map(calculate_bprr_od, agr['Traffic Type'], agr['start'], agr['end'], agr['WB Origin'], agr['WB Destination']))




agr = agr.rename(
    columns={'2017Total Cars': no_of_cars, 'Average Net Weight': wt_per_car, 'STCC Description': commodity,
             'g_dist': shortline_dist, 'Interchange Road From': start_rr, 'Railroad Id': current_rr,
             'Interchange Road To': forwarded_rr, 'Traffic Type': inout,
             'o1': transfer_1, 'd1': transfer_2, 'o': origin, 'd': destination, "Average TMS Miles": all_dist})


agr = agr.drop(
    ['City Trip Start', 'City Trip End', 'State Trip Start', 'State Trip End', 'start', 'end', "WB Origin", "WB Destination"],
    axis=1)  # seasonality could be added later



agr[wt_per_car] = agr[wt_per_car]/2000


# preparing gnbc data
gnbc = GNBC
gnbc.replace({r'[^\x00-\x7F]+': ''}, regex=True, inplace=True)  # removing non-ascii characters

gnbc['online_od'] = gnbc['On-Line O/D County'] + ', ' + gnbc['On-Line O/D State']
gnbc['offline_od'] = gnbc['Off-Line O/D County'] + ', ' + gnbc['Off-Line O/D State']
for i in range(len(gnbc)):
    if gnbc['Inbound or Outbound or Bridge'].iloc[i] == 'Inbound':
        gnbc.at[i, 'rr1'] = gnbc['Interchange Railroad'].iloc[i]
        gnbc.at[i, 'o1'] = gnbc['Interchange Location'].iloc[i] + ", OK"
        gnbc.at[i, 'origin'] = gnbc['offline_od'].iloc[i]
        gnbc.at[i, 'destination'] = gnbc['online_od'].iloc[i]
    elif gnbc['Inbound or Outbound or Bridge'].iloc[i] == 'Outbound':
        gnbc.at[i, 'rr2'] = gnbc['Interchange Railroad'].iloc[i]
        gnbc.at[i, 'd1'] = gnbc['Interchange Location'].iloc[i] + ", OK"
        gnbc.at[i, 'origin'] = gnbc['online_od'].iloc[i]
        gnbc.at[i, 'destination'] = gnbc['offline_od'].iloc[i]
    else:  # local and bridge donot have enough information
        gnbc.at[i, 'rr2'] = np.nan
        gnbc.at[i, 'd1'] = np.nan
        gnbc.at[i, 'origin'] = np.nan
        gnbc.at[i, 'destination'] = np.nan
        gnbc.at[i, 'rr1'] = np.nan
        gnbc.at[i, 'o1'] = np.nan

gnbc = gnbc.drop(['online_od', 'offline_od', 'On-Line O/D County', 'On-Line O/D State',
                  'Off-Line O/D County', 'Off-Line O/D State', 'Interchange Location', 'Interchange Railroad',
                  "Local O/D", "Seasonality", 'On-Line O/D', 'Off-Line O/D', 'Unnamed: 15'],
                 axis=1)  # seasonality could be added later
gnbc['rr'] = 'gnbc'
gnbc = gnbc.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': shortline_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr, 'Inbound or Outbound or Bridge':inout,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

gnbc[wt_per_car] = gnbc[wt_per_car]
# gnbc.to_csv("gnbc.csv")
# done

# preparing INRR data
inrr = INRR[['2017 Carloads', 'Inbound or Outbound or Bridge', 'Typical Net (Lading) Weight per Car', 'Commodity',
             'Online Shipment Distance', 'Interchange Railroad', 'Interchange Location', 'On-Line O/D', 'Off-Line O/D', "Seasonality"]]
for i in range(len(inrr)):
    if inrr['Inbound or Outbound or Bridge'].iloc[i] == 'In':
        inrr.at[i, 'origin'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'rr1'] = inrr['Interchange Railroad'].iloc[i]
        inrr.at[i, 'o1'] = inrr['Interchange Location'].iloc[i]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Out':
        inrr.at[i, 'origin'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'rr2'] = inrr['Interchange Railroad'].iloc[i]
        inrr.at[i, 'd1'] = inrr['Interchange Location'].iloc[i]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Bridge':
        inrr.at[i, 'origin'] = inrr['Seasonality'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'rr1'] = inrr['Interchange Railroad'].iloc[i].split('-')[0]
        inrr.at[i, 'o1'] = inrr['Interchange Location'].iloc[i].split('-')[0]
        inrr.at[i, 'rr2'] = inrr['Interchange Railroad'].iloc[i].split('-')[1]
        inrr.at[i, 'd1'] = inrr['Interchange Location'].iloc[i].split('-')[1]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Local':
        inrr.at[i, 'origin'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
    else:
        inrr.at[i, 'origin'] = np.nan
        inrr.at[i, 'dest'] = np.nan
        inrr.at[i, 'rr1'] = np.nan
        inrr.at[i, 'o1'] = np.nan
        inrr.at[i, 'rr2'] = np.nan
        inrr.at[i, 'd1'] = np.nan

inrr = inrr.drop(
    ['On-Line O/D', 'Off-Line O/D', 'Interchange Location', 'Interchange Railroad', "Seasonality"],
    axis=1)
inrr['rr'] = 'inrr'
inrr = inrr.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': shortline_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr, 'Inbound or Outbound or Bridge':inout,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

inrr[wt_per_car] = inrr[wt_per_car]

# done

# preparing KYLE
kyle = KYLE
kyle = kyle[
    ['From Station/Road', 'To Station/Road', 'STCC', 'AVERAGE WEIGHT', 'Origin State',
     'Origin Station', 'Destination Station', 'Destination State', 'ROUTE ONLINE MILES', 'TYPE OF TRAFFIC']]
kyle['o1'] = kyle['Origin Station'].str.strip() + ', ' + kyle['Origin State']
kyle['d1'] = kyle['Destination Station'].str.strip() + ', ' + kyle['Destination State']

kyle = kyle.drop(['Origin Station', 'Origin State', 'Destination Station', 'Destination State'], axis=1)

kyle = kyle.rename(columns={'AVERAGE WEIGHT': total_wt, 'STCC': commodity, 'TYPE OF TRAFFIC': inout,
                            'ROUTE ONLINE MILES': shortline_dist, 'From Station/Road': start_rr,
                            'To Station/Road': forwarded_rr, 'o1': origin, 'd1': destination, "TMS Miles": all_dist})
kyle = kyle.replace('Missing', np.nan)
kyle[total_wt] = kyle[total_wt]/2000
kyle['rr'] = 'kyle'
kyle[no_of_cars] = 1

# done


#SJVR
sjvr = SJVR
sjvr = sjvr[
    ['TYPE OF TRAFFIC','Commodity Name', 'Average weight', 'Origin Station', 'Origin State', 'Interchange Road',
     'Interchange Station', 'Dest Station', 'Dest State', 'Car Count', 'ROUTE ONLINE MILES',
     'TOTAL ONLINE MILES']]
sjvr['oo'] = sjvr['Origin Station'].str.rstrip() + ', ' + sjvr['Origin State']
sjvr['dd'] = sjvr['Dest Station'].str.rstrip() + ', ' + sjvr['Dest State']

sjvr['rr1'] = ''
sjvr['rr2'] = ''
sjvr['o1'] = ''

for i in range(len(sjvr)):
    if sjvr['TYPE OF TRAFFIC'].iloc[i] == 'ORIGINATING':
        sjvr.at[i, 'rr2'] = sjvr['Interchange Road'].iloc[i]
        sjvr.at[i, 'd1'] = sjvr['Interchange Station'].iloc[i]
    elif sjvr['TYPE OF TRAFFIC'].iloc[i] == 'TERMINATING':
        sjvr.at[i, 'rr1'] = sjvr['Interchange Road'].iloc[i]
        sjvr.at[i, 'o1'] = sjvr['Interchange Station'].iloc[i]
    else:
        sjvr.at[i, 'rr1'] = np.nan
        sjvr.at[i, 'rr2'] = np.nan
        sjvr.at[i, 'o1'] = np.nan
        sjvr.at[i, 'd1'] = np.nan

sjvr = sjvr.drop(['Origin Station', 'Origin State', 'Dest Station', 'Dest State', 'Interchange Road', 'Interchange Station'], axis=1)

sjvr = sjvr.rename(columns={'Car Count': no_of_cars, 'Average weight': wt_per_car, 'Commodity Name': commodity,
                            'ROUTE ONLINE MILES': shortline_dist, 'Interchange Road From': start_rr, 'rr': current_rr, 'TYPE OF TRAFFIC':inout,
                            'Interchange Road To': forwarded_rr, 'oo': origin, 'dd': destination, 'TOTAL ONLINE MILES': all_dist})
sjvr['rr'] = 'sjvr'
sjvr[wt_per_car] = sjvr[wt_per_car]/2000


# def get_rr_location(ibob,raj):
#     if ibob =='In':
#         return (raj.split(' ')[0], np.nan, np.nan, np.nan )
#     elif ibob == 'Out':
#         try:
#             return (np.nan, raj.split(' ')[1], np.nan, np.nan )
#         except:
#             return (np.nan, np.nan, np.nan, np.nan )
#     else:
#         return (np.nan, np.nan, np.nan, np.nan )




# preparing WSOR
wsor = WSOR
# the bridge data has 0 tons so removed
wsor = wsor[wsor['IB/OB'] != 'BRIDGE'] #sincethe tons for all the bridge traffic equals 0
# wsor = wsor.dropna() #removing "Total" calculated in the excel file, lets not be that aggressive
wsor['Commodity'] = wsor['Commodity'].str.split('-',1).str[0]

#wsor['rr1'], wsor['rr2'], wsor['o1'], wsor['d1'] = zip(*wsor.apply(lambda x: get_rr_location(x['IB/OB'], x['Road & Junctions']), axis = 1))



#Still cant figure out why this didnt work
# for i in range(len(wsor)):
#     if wsor['IB/OB'].iloc[i] == 'In':
#         wsor.at[i, 'rr1'] = wsor['Road & Junctions'].iloc[i].split(' ')[0]
#         wsor.at[i, 'o1'] = np.nan
#     elif wsor['IB/OB'].iloc[i] == 'Out':
#         try:
#             wsor.at[i, 'rr2'] = wsor['Road & Junctions'].iloc[i].split(' ')[1]
#         except:
#             wsor.at[i, 'rr2'] = np.nan
#         wsor.at[i, 'd1'] = np.nan
#     else:
#         print ("This will never print")
#         pass

wsor = wsor.rename(columns={'Total Cars': no_of_cars, 'Tons': total_wt, 'Commodity': commodity,
                            'Miles': all_dist, 'rr1': start_rr, 'rr': current_rr, 'IB/OB':inout,
                            'Destination	D-Rd': forwarded_rr, 'Online origin': transfer_1, 'online destination': transfer_2, 'Origin': origin,
                            'Destination': destination, 'MilesonRR': shortline_dist})

drop_columns = ['Description', 'Traffic Type', 'D-Rd', 'O-Rd', 'Road & Junctions', 'Seasonality', 'o1_', 'd1_' ]

wsor = wsor.drop(drop_columns, axis=1)

# data with total removed
wsor[commodity] = wsor[commodity].fillna('N/A')
wsor = wsor[~wsor[commodity].str.contains("Total")]
wsor[commodity == 'N/A'] = np.nan
wsor[destination] = wsor[destination].replace(',   ', np.nan)
wsor['rr'] = 'wsor'


# wsor.to_csv("wsor.csv")

# preparing YSVR
# total weight given, weight per car not given
ysvr = YSVR[['STCC', 'ORIGIN', 'DEST', 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04',
             "ROUTE ROAD 05", "NET WEIGHT", "MILES", ]]
ysvr['rrlist'] = [
    row['ROUTE ROAD 01'] + "," + row['ROUTE ROAD 02'] + "," + row['ROUTE ROAD 03'] + "," + row['ROUTE ROAD 04'] + "," +
    row['ROUTE ROAD 05'] for index, row in ysvr.iterrows()]
ysvr['rr1'] = ''
ysvr['rr2'] = ''
for i in range(len(ysvr)):
    ysvr.at[i, 'rr1'], ysvr.at[i, 'rr2'] = get_rr1_rr2(ysvr['rrlist'].iloc[i])

ysvr = ysvr.drop(["rrlist", 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04', "ROUTE ROAD 05"],
                 axis=1)

ysvr['inout'] = ysvr['ORIGIN'].map(get_inout)

ysvr = ysvr.rename(columns={'NET WEIGHT': total_wt, 'STCC': commodity,
                            'MILES': all_dist, 'rr1': start_rr, 'rr': current_rr, 'inout':inout,
                            'Destination	D-Rd': forwarded_rr, 'o1': transfer_1, 'd1': transfer_2, 'ORIGIN': origin,
                            'DEST': destination})

ysvr[total_wt] = ysvr[total_wt]/2000
ysvr[shortline_dist] = 1
ysvr[no_of_cars] = 1
ysvr['rr'] = 'ysvr'



# adding all to one
all = wsor.append(acwr).append(agr).append(gnbc).append(inrr).append(kyle).append(sjvr).append(ysvr)

#all = wsor.append(acwr).append(agr).append(fmrc).append(gnbc).append(inrr).append(kyle).append(sjvr).append(wsor).append(ysvr)
# all maths
#
# all = all[all[commodity].notnull()] #commodity cant be null

#all = all[all[wt_per_car].notnull()]
#all = all[all[shortline_dist].notnull()]
# all = all[all[origin].notnull()]
# all = all[all[destination].notnull()]
all = all.reset_index()
all = all.drop(['index'], axis = 1)

all.to_csv("intermediate/shortlines_output_raw.csv")







