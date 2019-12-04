import argparse
import os
import datetime

options = argparse.ArgumentParser()
options.add_argument('--pid', required=True)
options.add_argument('--date', required=True)
options.add_argument('--dir-type', required=True)
options.add_argument('--file-name', default=None)
options.add_argument('--seg-name', default=None)
options.add_argument('--seg-num', default=None)
options.add_argument('--root-name', default='/mnt/an-ss-mix/SS-MIX2-ROOT/')


class Get_data:
    
    '''指定した条件の位置にある記述を返す'''

    def __init__(self, pid, date, dir_type, file_name, root_name):

        self.pid = pid
        self.date = date
        self.dir_type = dir_type
        self.file_name = file_name
        self.root_name = root_name

    def return_line(self, path, seg_name, seg_num):
        
        with open(path, mode='r', encoding='iso-2022-jp') as f:
            lines = f.readlines()
            for line in lines:
                if seg_name!=None:
                    if line.split("|")[0]==seg_name:
                        if seg_num!=None:
                            return line.split("|")[int(seg_num)]
                        else:
                            return line
                else:
                    if seg_num!=None:
                        return line.split("|")[int(seg_num)]
                    else:
                        return line
   
    def print_line(self, path, seg_name, seg_num):

        with open(path, mode='r', encoding='iso-2022-jp') as f:
            lines = f.readlines()
            for line in lines:
                if seg_name!=None:
                    if line.split("|")[0]==seg_name:
                        if seg_num!=None:
                            print(line.split("|")[int(seg_num)])
                        else:
                            print(line)
                else:
                    if seg_num!=None:
                        print(line.split("|")[int(seg_num)])
                    else:
                        print(line)

 
    def return_data(self, seg_name, seg_num):

        if self.file_name!=None:
            path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid+'/'+str(self.date)+'/'+self.dir_type+'/'+self.file_name
            return self.return_line(path,seg_name,seg_num)
            
        else:
            path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid+'/'+str(self.date)+'/'+self.dir_type
            files = os.listdir(path)
            files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
            files_file = [f for f in files_file if str(f)[-1]!=0]
            if len(files_file)==1:
                return self.return_line(os.path.join(path,files_file[0]),seg_name,seg_num)
            elif len(files_file)>1:
                results = []
                for f in files_file:
                     results.append(self.return_line(os.path.join(path,f),seg_name,seg_num))
                return results
    
    def print_data(self, seg_name, seg_num):

        if self.file_name!=None:
            path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid+'/'+str(self.date)+'/'+self.dir_type+'/'+self.file_name
            print(self.return_line(path,seg_name,seg_num))

        else:
            path = self.root_name+self.pid[:3]+'/'+self.pid[3:6]+'/'+self.pid+'/'+str(self.date)+'/'+self.dir_type
            files = os.listdir(path)
            files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
            files_file = [f for f in files_file if str(f)[-1]!=0]
            for f in files_file:
                self.print_line(os.path.join(path,f),seg_name,seg_num)
                

def main(opt):

    data = Get_data(opt.pid,opt.date,opt.dir_type,opt.file_name,opt.root_name)
    data.print_data(opt.seg_name,opt.seg_num)
    
    exit(0)

if __name__ == '__main__':
    main(options.parse_args())


