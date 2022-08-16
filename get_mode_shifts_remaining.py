import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from variables import *
from get_mode_shifts import *



# get_share(args)
def get_share1(args):
    global _compare_
    dist = 1000 #the distance doesnt matter
    commodty, rr, _dist_, start_coord, end_coord, transfer_pt1, transfer_pt2, ann_tonnage, nos = args[0], args[1], args[2], args[3],  args[4], args[5] , args[6], args[7], args[8]
    rl_rate_p_tm = get_rail_rate(dist, commodty)
    truck_rate_pton_const_all = get_truck_rates(_dist_, _compare_)
    #
    ttype_int = int(
        (commodty_distr_df[commodty_distr_df.SCTG == int(commodty[1:-1])]["Trailer type"]).map(type_conversion_dict))
    truck_rate_pton_const = [truck_rate_pton_const_all[ttype_int]] + [truck_rate_pton_const_all[ttype_int + 3]]
    cost = [rl_rate_p_tm * ann_tonnage * _dist_, truck_rate_pton_const[0] * ann_tonnage,
            truck_rate_pton_const[1] * ann_tonnage]
    # calculation
    min_cpcr = np.where(_dist_ <= 10, 200, min_cost_pcar)
    if cost[0] <= min_cpcr * nos:
        cost[0] = min_cpcr * nos
    Ur, Ut = get_utilities(cost, commodty, _dist_)
    # print cost
    pr = [1 - 1.0 / (1 + np.exp(Ur - x)) for x in Ut]
    return cost[0], cost[1], cost[2], Ur, Ut[0], Ut[1], pr[0], pr[1], rl_rate_p_tm, truck_rate_pton_const[0], \
           truck_rate_pton_const[1]


def get_remaining_tons(comm, dist, _rr_, nos, _use_rate):
    global _compare_
    #comm, dist, _rr_, nos, _use_rate = '"02"' , 852.5000, 'wsor', 720, 74762.6535
    base_case = 'pred1'  # the remanining tons from 'pred1' would be used
    base_data_df = pd.read_csv("./output/mode_split_{0}_0_{1}.csv".format(base_case, _compare_))
    base_data_df['use_rate1'] = base_data_df[use_rate] - base_data_df['lost_ton']
    use_rate_val = base_data_df.loc[(base_data_df[commodity]==comm) &
                                    (base_data_df[google_maps_dist]==dist) &
                                    (base_data_df[current_rr]==_rr_) &
                                    (base_data_df[no_of_cars]==nos) &
                                    (base_data_df[use_rate]==_use_rate), "use_rate1"].values[0]
    return use_rate_val



def get_remaining_tons_replaced():
    #
    base_case = 'pred1' # for column order
    comm_list = ['"02"', '"11"', '"12"', '"13"', '"14"', '"15"', '"16"', '"17"', '"18"', '"19"', '"20"', '"22"', '"24"', '"25"', '"26"', '"27"', '"31"', '"32"', '"41"']
    #
    wt_threshold = 5000 #250 cars
    d_df = pd.read_csv("input/shortlines_output_all_unique_ods.csv") #source of all data
    col_order = list(pd.read_csv("./intermediate/"+ base_case + ".csv").columns)
    #col_order = [shortline_dist if x == google_maps_dist else x for x in col_order]
    col_order.remove("Unnamed: 0")
    #
    #records with more than 5000 criteria (this is the trigger)
    #
    d_df[shortline_dist] = d_df[shortline_dist].replace("Null", np.nan).astype(float)
    data1 = d_df[(d_df[total_wt] >= wt_threshold) &  (d_df[commodity].isin(comm_list)) & ((d_df[google_maps_dist] - d_df[shortline_dist]  >=600)) &(d_df[shortline_dist] <= 50)]
    #
    data1.to_csv("./intermediate/pred2a_{0}_1_trigger.csv".format(_compare_))
    #
    data3 = d_df.copy()
    #
    #all_data, origin or destination removed (based on the transfer point)
    data3 = data3.replace("Null", "")
    data3 = data3[~((data3[transfer_1] == "") & (data3[transfer_2] == ""))] #both transfers cant be missing
    data3[start_coord] = np.where(data3[transfer_1] != "", "", data3[start_coord])
    data3[end_coord] = np.where(data3[transfer_2] != "", "", data3[end_coord])
    #
    data1 = data1.replace("Null", "")
    data1 = data1[~((data1[transfer_1] == "") & (data1[transfer_2] == ""))] #both transfers cant be missing
    data1[start_coord] = np.where(data1[transfer_1] != "", "", data1[start_coord])
    data1[end_coord] = np.where(data1[transfer_2] != "", "", data1[end_coord])
    #
    on_keep = [start_coord,end_coord, commodity, current_rr, transfer_1, transfer_2, shortline_dist]
    common = data3.merge(data1,on=on_keep)[on_keep].drop_duplicates()
    data4 = data3.merge(common,on= on_keep, how='inner')
    data4["new_use_rate"] = map(get_remaining_tons, data4[commodity], data4[google_maps_dist], data4[current_rr],
                                data4[no_of_cars], data4[total_wt])
    #
    data4.to_csv("./intermediate/pred2a_{0}_2_smaller_shpments_added.csv".format(_compare_))
    #
    #
    data4 = data4[
        [start_coord, end_coord, commodity, current_rr, transfer_1, transfer_2, no_of_cars, "new_use_rate", shortline_dist,
         google_maps_dist]]  # remove columns from y
    data5 = pd.pivot_table(data4, values=["new_use_rate", no_of_cars], index=[commodity, current_rr, shortline_dist,start_coord, end_coord, transfer_1, transfer_2],
                           aggfunc={"new_use_rate": np.sum, no_of_cars: np.sum}).reset_index()
    data5 = data5.rename(columns={"new_use_rate": use_rate})
    data5.to_csv("./intermediate/pred2a_{0}_3_combined.csv".format(_compare_))
    return data5

for _compare___ in compare:
    global _compare_
    _compare_ = _compare___
    print _compare_
    data_df = get_remaining_tons_replaced()
    # data_df1[['Ur','Ut0','Ut1','pt0','pt1']] = zip(*data_df.apply(get_share, axis = 1))
    data_df['costr'], data_df['cost0'], data_df['cost1'], data_df['Ur'], data_df['Ut0'], data_df['Ut1'], data_df[
        'pr0'], \
    data_df['pr1'], data_df['rl_rate_ptm'], data_df['truck_rate1'], data_df['truck_rate2'] = zip(*data_df.apply(get_share1, axis=1))
    # data_df['tr_addi'] = data_df['pt1'] - data_df['pt0']
    data_df['percent_lost'] = (1 - data_df['pr1'] / data_df['pr0'])
    data_df['percent_lost'].fillna(0, inplace=True)
    data_df['lost_ton'] = data_df['use_rate'] * data_df['percent_lost']
    data_df['lost_rev'] = data_df['percent_lost'] * data_df['nos'] * np.where(data_df[shortline_dist] <= 10, 200, 325)  # change based on the distance <10
    data_df['pcent_div'] = data_df['lost_ton'] / data_df['use_rate']
    data_df.to_csv("./output/mode_split_{0}_{1}_{2}.csv".format(_compare_, base, _compare_))
