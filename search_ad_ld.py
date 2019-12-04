#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import ld_admission
import numpy as np
import pandas as pd
import datetime
import pickle

options = argparse.ArgumentParser()
options.add_argument('--start', default=0)
options.add_argument('--end', default=99999999)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')
options.add_argument('--func')

def get_dir(root_name):

    path = root_name
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]

    return files_dir

def count_pid(root_name):
    
    count=0
    pid_list=[]
    files_list = get_dir(root_name)
    for i in files_list:
        path_2 = os.path.join(root_name, i)
        files_list_2 = get_dir(path_2)
        for j in files_list_2:
            path_3 = os.path.join(path_2, j)
            pids = get_dir(path_3)
            if pids==[""] or pids==[]:
                continue
            #print(pids)
            pid_list.append(pids)
            count += len(pids)
            if count%10000 == 0:
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),count,"/","1195689","were finished")
    pid_list = np.concatenate(pid_list)
    with open('pid_list.txt', mode='wb') as fo:
        pickle.dump(pid_list, fo)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Count was finished. patient num = ", count)
    return pid_list

def import_list(filename):
    with open(filename, mode='rb') as fi:
        pid_list = pickle.load(fi)
    return pid_list

def search_pid(start,end,root_name,count):
    
    ad_ld_df = pd.DataFrame(index=[],columns=["年齢","性別","退院時状態","入院期間","入院時刻"])
    num = 0
    files_list = get_dir(root_name)
    for i in files_list:
        path_2 = os.path.join(root_name, i)
        files_list_2 = get_dir(path_2)
        for j in files_list_2:
            path_3 = os.path.join(path_2, j)
            pids = get_dir(path_3)
            for k in pids:
                df = ld_admission.ad_ld_data_df(k,start,end,root_name)
                ad_ld_df = pd.concat([ad_ld_df,df]).reset_index(drop=True)
                num += 1
                if num%100 == 0:
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),num,"/","1195689","were finished") 
    
    ad_ld_df.to_csv("ad_ld.csv")


def make_ld_df(pid_list,start,end,root_name):
    ad_ld_df = pd.DataFrame(index=[],columns=["年齢","性別","退院時状態","入院期間","入院時刻"])
    num = 0
    new_num = 0
    for pid in pid_list:
        df = ld_admission.ad_ld_data_df(pid,start,end,root_name)
        ad_ld_df = pd.concat([ad_ld_df,df]).reset_index(drop=True)
        if num%1000 == 0:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),num,"/","1195689","were finished") 
        if num%20000 == 0 and num != 0:
            filename = "results/ad_ld_"+str(new_num)+"-"+str(num)+".csv"
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"saving ",filename)
            ad_ld_df.to_csv(filename) 
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"file was saved as ",filename)
            ad_ld_df = pd.DataFrame(index=[],columns=["年齢","性別","退院時状態","入院期間","入院時刻"])
            new_num = num + 1
        num +=1
    filename = "results/ad_ld_"+str(new_num)+"-"+str(num)+".csv"
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"saving file ",filename)
    ad_ld_df.to_csv(filename)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"file was saved as ",filename)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),num,"/","1195689","were finished")    

def main(opt):
    
    if opt.func == "0":
        start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " program start"
        print(start)
        print(count_pid(opt.root_name))
    elif opt.func == "1":
        start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " program start"
        print(start)
        pid_list = import_list("pid_list.txt")
        make_ld_df(pid_list,opt.start,opt.end,opt.root_name)
    #start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " program start"
    #print(start)
    #print(count_pid(opt.root_name))
    #print(count)
    #print(import_list("pid_list.txt"))
    #count = 1195689
    #search_pid(opt.start,opt.end,opt.root_name,count) 

    exit(0)

if __name__ == '__main__':
    main(options.parse_args())

