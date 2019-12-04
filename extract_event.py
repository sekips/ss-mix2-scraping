#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import extract_date
import extract_data
import numpy as np
import pickle


options = argparse.ArgumentParser()
options.add_argument('--pid', default=None)
options.add_argument('--start', default=0)
options.add_argument('--end', default=99999999)
options.add_argument('--dir-type', default=None)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')

def detect_event(pid, start, end, dir_type, root_name):
    
    date_filter = extract_date.Date_filter(pid, start, end, dir_type, root_name)
    date_list = date_filter.filtered_by_file_type()
    date_list.sort()
    return date_list

def detect_ad_time(pid, date_list, root_name):
    
    ad_time_list = []
    if len(date_list)==0:
        return ad_time_list
    else:
        for date in date_list:
            data_file = extract_data.Get_data(pid,date,"ADT-22",None,root_name)
            ad_time = data_file.return_data("PV1",44)
            if type(ad_time) is not list:
                ad_time = [ad_time]
            ad_time_list.append(ad_time)
        if len(ad_time_list)==0:
            return ad_time_list
        else:
            if [""] in ad_time_list:
                ad_time_list.remove([""])
            
            if len(ad_time_list)==0:
                return ad_time_list
            else:
                ad_time_list = np.concatenate(ad_time_list).tolist()
                if "" in ad_time_list:
                    ad_time_list.remove("")
                
                if len(ad_time_list)==0:
                    return ad_time_list
                else:
                    ad_time_list = [int(x.replace('\n','')) for x in ad_time_list]
                    ad_time_list.sort()
                    return ad_time_list

def detect_ent_time(pid, date_list, root_name):
    
    ent_time_list = []
    if len(date_list)==0:
        return ent_time_list
    else:
        for date in date_list:
            data_file = extract_data.Get_data(pid,date,"ADT-52",None,root_name)
            ent_time = data_file.return_data("PV1",45)
            if type(ent_time) is not list:
                ent_time = [ent_time]
            ent_time_list.append(ent_time)
        if len(ent_time_list)==0:
            return ent_time_list
        else:
            if [""] in ent_time_list:
                ent_time_list.remove([""])

            if len(ent_time_list)==0:
                return ent_time_list
            else:
                ent_time_list = np.concatenate(ent_time_list).tolist()
                if "" in ent_time_list:
                    ent_time_list.remove("")
                
                if len(ent_time_list)==0:
                    return ent_time_list
                else:
                    ent_time_list = [int(x.replace('\n','')) for x in ent_time_list]
                    ent_time_list.sort()
                    return ent_time_list

def import_list(filename):
    with open(filename, mode='rb') as fi:
        pid_list = pickle.load(fi)
    return pid_list



def main(opt):
    
    #print(detect_event(opt.pid,opt.start,opt.end,opt.dir_type,opt.root_name))
    
    pid_list = import_list("pid_list.txt")
    for pid in pid_list:
        print(pid)
        print("入院予約: ",detect_event(pid,opt.start,opt.end,"ADT-21",opt.root_name))
        print("入院実施: ",detect_event(pid,opt.start,opt.end,"ADT-22",opt.root_name))
    #print("ad_date: ",detect_event(opt.pid,opt.start,opt.end,"ADT-22",opt.root_name))
    #print("ent_date: ",detect_event(opt.pid,opt.start,opt.end,"ADT-52",opt.root_name))
    #print("ad_time: ",detect_ad_time(opt.pid,detect_event(opt.pid,opt.start,opt.end,"ADT-22",opt.root_name),opt.root_name))
    #print("ent_time: ",detect_ent_time(opt.pid,detect_event(opt.pid,opt.start,opt.end,"ADT-52",opt.root_name),opt.root_name))


if __name__ == '__main__':
    main(options.parse_args())
