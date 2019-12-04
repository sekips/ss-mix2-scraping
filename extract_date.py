#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os

options = argparse.ArgumentParser()
options.add_argument('--pid', required=True)
options.add_argument('--start', default=0)
options.add_argument('--end', default=99999999)
options.add_argument('--dir-type', default=None)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')

class Date_filter:

    '''特定の名前のディレクトリが存在する日付をリストとして抽出する'''
  
    def __init__(self, pid, start, end, dir_type, root_name):
    
        self.pid = pid
        self.start = start
        self.end = end
        self.dir_type = dir_type
        self.root_name = root_name
        
    def get_dir(self):
        
        '''HL7のファイルが存在する全ての日付を抽出'''
 
        path = self.root_name + self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid
        files = os.listdir(path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        
        return files_dir

    def filtered_by_date_range(self):

        '''抽出した日付から、範囲指定したものだけを抽出'''

        int_list = self.get_dir()
        int_list.remove('-')
        int_list = [int(x) for x in int_list]
        date_list = [x for x in int_list if (x >= self.start) and  (x <= self.end)]

        return date_list

    def filtered_by_file_type(self):
        
        '''ディレクトリ名の指定があれば、そのディレクトリが下層に存在する日付のみを抽出する'''

        if self.dir_type == None:
            return self.filtered_by_date_range()
        else:
            filtered_date_list = []
            path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid

            for i in self.filtered_by_date_range():
                path_tmp = os.path.join(path,str(i))
                files = os.listdir(path_tmp)
                files_dir = [f for f in files if os.path.isdir(os.path.join(path_tmp, f))]
                if self.dir_type in files_dir:
                    filtered_date_list.append(i)
            return filtered_date_list

def main(opt):
    
    date_filter = Date_filter(opt.pid,opt.start,opt.end,opt.dir_type,opt.root_name)
    return date_filter.filtered_by_file_type()

if __name__ == '__main__':
    main(options.parse_args())
