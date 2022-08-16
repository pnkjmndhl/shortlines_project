import csv
import pandas as pd
import numpy as np

#Note: To convert rows from sas to python, (x-1,y)


distance_bins = [50,100,200,400,600,800,1000,1200]


def f(a,b):
    class1 = [103,105,400,555,712,777,802,978]
    if a in class1:
        if b in class1:
            return 1
    else:
        return 0




def get_dist_bin(val):
    diff_list = [abs(x - val) for x in distance_bins]
    min_val = min(diff_list)
    _index_ = diff_list.index(min_val)
    return distance_bins[_index_]


def get_commo(value):
    value = str(value)
    if value[0] == '"':
        value = value[1:-1]
    value4 = '"' + value[0:4] +'"'
    value5 = '"' + value[0:5] +'"'
    try: #search value4, if not found, use value5
        dumm =  stcg_dict[value4]
        if dumm == '""': #if dumm is empty
            raise ValueError('Bro, did not find')
        found_dict[value] = dumm
        return dumm
    except:
        try:
            dumm = stcg_dict[value5]
            found_dict[value] = dumm
            return dumm
        except:
            value = '"' + value +'"'
            #if not found in both use the 49 dictionary
            try:
                dumm = stcg_49_dict[value]
                found_dict[value] = dumm
                return dumm
            except:
                not_found_dict[value] = [value4, value5]


#file = open("CWS16UM.txt").readlines()
file = open("WB2018_900_Unmasked.txt").readlines()
#file[1]->line1


d= {}
for i in range(len(file)):
    d.setdefault('wayser', []).append(file[i][0:6])
    d.setdefault('tdis', []).append(file[i][534:539])
    d.setdefault('uton', []).append(file[i][383:390])
    d.setdefault('ucar', []).append(file[i][26:30])
    d.setdefault('expn', []).append(file[i][350:353])
    d.setdefault('xcar', []).append(file[i][377:383])
    d.setdefault('urev', []).append(file[i][82:91])
    d.setdefault('zvar', []).append(file[i][50:51])
    d.setdefault('orr', []).append(file[i][157:160])
    d.setdefault('trr', []).append(file[i][213:216])
    d.setdefault('stcc', []).append(file[i][310:317])
    d.setdefault('ofip', []).append(file[i][563:568])
    d.setdefault('tfip', []).append(file[i][568:573])




df = pd.DataFrame.from_dict(d)


df.orr = df.orr.astype(np.int64)
df.trr = df.trr.astype(np.int64)
df.stcc = df.stcc.astype(np.int64)
df.ofip = df.ofip.astype(np.int64)
df.tfip = df.tfip.astype(np.int64)
df.tdis = df.tdis.astype(np.float64)
df.uton = df.uton.astype(np.float64)



#montgomery, NC->37123
#moore, NC->37125\
df1 = df[((df.tfip == 37123) | (df.tfip == 37125))]

#only pulpwood chips and pine


df1.to_csv("2018waybill.csv")

origins_ = list(df1.ofip.unique())

tons_ = df1.uton.astype(int).sum()
tons_to_get = 2783*104


