######mi_phy_processing.py#########
#==============instructions==============
###### This file can process all the mi_phy csv files under a directory.
###### After processing, the new csv files end with _new.csv can successfully be read by Python pandas 
###### Ex. python3 csv_processing.py DIRRECTORY_NAME

import os
import sys

dirname = sys.argv[1]
filenames = os.listdir(dirname)

csv_files = []
for filename in filenames:
    if filename.endswith("_ml1.csv"):
        csv_files.append(os.path.join(dirname, filename))
    if filename.endswith("_pcap.csv"):
        csv_files.append(os.path.join(dirname, filename))


for csv_file in csv_files:
    print(csv_file)
    print("csv process >>>>>")

    f = open(csv_file, 'r')
    lines = f.readlines()
    #第一次讀檔案,找最長的列
    if csv_file.endswith("_pcap.csv"):
        fnew = open(csv_file[:-4]+"_new.csv", 'w')

        for line in lines:
            l = line.split('@')
            for i in range(len(l)):
                if l[i] == '':
                    l[i] = '-'
                elif l[i] == '\n':
                    l[i] = '-\n'
            x = ''
            for i in l:
                x += i + '@'
            fnew.write(x[:-1])

    else:
        max_row_size = 0
        for line in lines:
            row_size = line.count(",")+1
            if row_size > max_row_size:
                max_row_size = row_size
        
        fnew = open(csv_file[:-4]+"_new.csv", 'w')
        #第二次讀檔，將舊檔資料寫入新檔
        for line in lines:
            row_size = line.count(",") + 1
            append_line = line[:-1]
            for i in range(max_row_size - row_size):
                append_line = append_line + ",-"
            append_line = append_line + "\n"
            fnew.write(append_line)


    f.close()
    os.system(f"rm {csv_file}")
    fnew.close()