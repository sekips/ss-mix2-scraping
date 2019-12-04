#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import datetime
import numpy as np
import pandas as pd

options = argparse.ArgumentParser()
options.add_argument('--pid', required=True)
options.add_argument('--date', required=True)
options.add_argument('--dir-type', default="OML-11")
options.add_argument('--test-name', default=None)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')

class Get_ld_results:
      
    '''日付を指定し存在する検査結果を出力'''
 
    def __init__(self, pid, date, dir_type, test_name, root_name):
    
        self.pid = pid
        self.date = date
        self.dir_type = dir_type
        self.test_name = test_name
        self.root_name = root_name
    
    def partition(self, line):

        '''HL7のテキスト内から検査項目、結果、単位、検体採取時間を抽出'''

        obx_list = line.split("|")
        exam_name = obx_list[3].split("^")[1]
        value = obx_list[5]
        exam_time = obx_list[14]
        if len(exam_time)<10:
            exam_time = "19000101000000"
        exam_time = datetime.datetime.strptime(exam_time.replace('\n','').ljust(14, '0'), '%Y%m%d%H%M%S')
        if exam_name!=None and obx_list[5]!=None:
            if obx_list[6]!=None:
                unit = obx_list[6].split("^")[0]
            else:
                unit = None
            return exam_time,exam_name,unit,value

    def return_results(self,date):
        
        '''検査結果の指定があればその項目の結果のみをデータフレーム形式で返す'''
        
        ld_results_df = pd.DataFrame(index=[], columns=["time","exam","value","unit"])
        path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid+'/'+date+'/'+self.dir_type
        try:
            files = os.listdir(path)
            files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
            files_file = [f for f in files_file if str(f)[-1]!=0]
       
            for f in files_file:
                with open(os.path.join(path,f),mode='r',encoding='iso-2022-jp') as f:
                    lines = f.readlines()
                    for line in lines:
                        if self.test_name!=None:
                            if line.split("|")[0]=="OBX" and line.split("|")[2]!="CWE" and line.split("|")[3].split("^")[1]==self.test_name:
                                exam_time,exam_name,unit,value = self.partition(line)
                                ld_results_df = pd.concat([ld_results_df,pd.DataFrame({"exam":exam_name + "__" +unit,
                                                                                   "value":value,
                                                                                   "unit":unit,
                                                                                   "time":exam_time},index=[0],columns=["time","exam","value","unit"])],axis=0).reset_index(drop=True)
                            
                        else:
                            if line[:3]=="OBX" and line.split("|")[2]!="CWE":
                                exam_time,exam_name,unit,value = self.partition(line)
                                ld_results_df = pd.concat([ld_results_df,pd.DataFrame({"exam":exam_name + "__" +unit,
                                                                                   "value":value,
                                                                                   "unit":unit,
                                                                                   "time":exam_time},index=[0],columns=["time","exam","value","unit"])],axis=0).reset_index(drop=True)

        except FileNotFoundError:
            pass
        
        return ld_results_df 

def main(opt):
    
    ld_detector = Get_ld_results(opt.pid,opt.date,opt.dir_type,opt.test_name,opt.root_name)
    return ld_detector.return_results(opt.date)

    exit(0)

if __name__ == '__main__':
    main(options.parse_args())
