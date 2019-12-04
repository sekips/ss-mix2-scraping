#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import extract_event
import extract_data
import get_ld 
import datetime
import pandas as pd
import numpy as np

options = argparse.ArgumentParser()
options.add_argument('--pid', required=True)
options.add_argument('--start', default=0)
options.add_argument('--end', default=99999999)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')


def ad_date(pid,start,end,root_name):
    ad_date_list = extract_event.detect_event(pid,start,end,"ADT-22",root_name)
    return ad_date_list

def ent_date(pid,start,end,root_name):
    ent_date_list = extract_event.detect_event(pid,start,end,"ADT-52",root_name)
    return ent_date_list

def ad_time(pid,date_list,root_name):
    return extract_event.detect_ad_time(pid,date_list,root_name)

def ent_time(pid,date_list,root_name):
    return extract_event.detect_ent_time(pid,date_list,root_name)

def make_ad_df(pid,date,root_name):
    ld_results = get_ld.Get_ld_results(pid,date,"OML-11",None,root_name)
    df = ld_results.return_results(str(date))
    df_pre = ld_results.return_results((datetime.datetime.strptime(str(date), '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d'))
    df_post = ld_results.return_results((datetime.datetime.strptime(str(date), '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d'))
    df = pd.concat([df_pre,df,df_post]).reset_index(drop=True)
    return df

def return_ad_time(pid,date,root_name):
    ad_file = extract_data.Get_data(pid,date,"ADT-22",None,root_name)
    ad_time = ad_file.return_data("PV1",44)
    ad_time = datetime.datetime.strptime(ad_time.replace('\n','').ljust(14, '0'), '%Y%m%d%H%M%S')
    return ad_time

def return_age_sex(pid,time,root_name):
    ad_file = extract_data.Get_data(pid,time[:8],"ADT-22",None,root_name)
    pt_birth = ad_file.return_data("PID",7)
    if type(pt_birth) is list:
        time_list = ad_file.return_data("PV1",44)
        time_list = [x.replace('\n','') for x in time_list]
        pt_birth = pt_birth[time_list.index(time)]
    pt_age = int((int(time[:8]) - int(pt_birth))/10000)
    pt_sex = ad_file.return_data("PID",8)
    if type(pt_sex) is list:
        time_list = ad_file.return_data("PV1",44)
        time_list = [x.replace('\n','') for x in time_list]
        pt_sex = pt_sex[time_list.index(time)]
    pt_room = ad_file.return_data("PV1",3)
    if type(pt_room) is list:
        time_list = ad_file.return_data("PV1",44)
        time_list = [x.replace('\n','') for x in time_list]
        pt_room = pt_room[time_list.index(time)]
    pt_dep = ad_file.return_data("PV1",6)
    if type(pt_dep) is list:
        time_list = ad_file.return_data("PV1",44)
        time_list = [x.replace('\n','') for x in time_list]
        pt_dep = pt_dep[time_list.index(time)]
    return pt_age, pt_sex, pt_room, pt_dep

def slice_ad_df(df,ad_time):
    df_sliced = df[(df['time'] >= (ad_time - datetime.timedelta(hours=6))) & (df['time'] <= (ad_time + datetime.timedelta(hours=6)))]
    df_sliced.loc[:,"time_to_ad"] = df_sliced.loc[:,"time"]-ad_time
    f_seconds = lambda x: abs(x.total_seconds())
    df_sliced.loc[:,"time_to_ad"] = df_sliced.loc[:,"time_to_ad"].apply(f_seconds)
    df_deduplicated = df_sliced.loc[df_sliced.groupby('exam')['time_to_ad'].idxmin()]
    return df_deduplicated

def get_ent_state(pid,ent_t,root_name):
    ent_d = ent_t//1000000
    ent_data = extract_data.Get_data(pid,ent_d,"ADT-52",None,root_name)
    ent_ds = ent_data.return_data("PV1",45)
    ent_states = ent_data.return_data("PV1",36)
    if type(ent_ds) is list:
        ent_ds = [int(x.replace('\n','')) for x in ent_ds]
        return ent_states[ent_ds.index(ent_t)]
    else:
        return ent_states

def ad_ld_data_df(pid,start,end,root_name):

    ad_time_list = ad_time(pid,ad_date(pid,start,end,root_name),root_name)
    ent_time_list = ent_time(pid,ent_date(pid,start,end,root_name),root_name)
    if len(ad_time_list)==0:
        pass

    else:
        ad_ld_df = pd.DataFrame(index=[],columns=["年齢","性別","退院時状態","入院期間","入院時刻","ID","入院病棟","退院時刻","入院科"])
 
        for t in ad_time_list:
            i = t//1000000
            ent_t_list = np.array(ent_time_list)[np.where(np.array(ent_time_list) >= t)]
            if len(ent_t_list.tolist())!=0:
                ent_t = min(ent_t_list)
                ent_state = get_ent_state(pid,ent_t,root_name)
                ent_t = datetime.datetime.strptime(str(ent_t), '%Y%m%d%H%M%S')
                ad_ld = make_ad_df(pid,i,root_name)
                ad_t =  datetime.datetime.strptime(str(t), '%Y%m%d%H%M%S')
                ad_period = (ent_t - ad_t).total_seconds()
                pt_age, pt_sex, pt_room, pt_dep = return_age_sex(pid,str(t),root_name)
                df = slice_ad_df(ad_ld,ad_t)
                df = pd.concat([df,pd.DataFrame({"exam":["年齢","性別","退院時状態","入院期間","入院時刻","ID","入院病棟","退院時刻","入院科"],
                                         "value":[pt_age,pt_sex,ent_state,ad_period,ad_t,pid,pt_room,ent_t,pt_dep],
                                         "unit":["歳",np.nan,np.nan,"sec",np.nan,np.nan,np.nan,np.nan,np.nan],
                                         "time":[ad_t,ad_t,ent_t,ent_t,ad_t,ad_t,ad_t,ent_t,ad_t],
                                         "time_to_ad":[0,0,ad_period,ad_period,0,0,0,ad_period,0]},index=[0,1,2,3,4,5,6,7,8],columns=["time","exam","value","unit","time_to_ad"])],axis=0).reset_index(drop=True)
                df = df.set_index("exam")
                ad_ld_df = pd.concat([ad_ld_df,df[["value"]].T.reset_index(drop=True)],axis=0)

        return ad_ld_df
    

def main(opt):

    df = ad_ld_data_df(opt.pid,opt.start,opt.end,opt.root_name)
    print(df)
    df.to_csv("test.csv")

    exit(0)

if __name__ == '__main__':
    main(options.parse_args())
