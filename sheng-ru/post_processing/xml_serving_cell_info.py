######xml_serving_cell_info.py#########
#==============instructions==============
######This file requires the txt file which is generated from offline_analysis.py with LTE_RRC_Serv_Cell_Info and mi2log file 
######The rows shows the information of each diag mode packets (dm_log_packet) from Mobile Insight 
######The columns are indicators about whether a packet has the type of the message

from bs4 import BeautifulSoup
import sys
import os
from itertools import chain

dirname = sys.argv[1]

filenames = os.listdir(dirname)

for fname in filenames:
    if fname[-4:] != '.txt':
        continue
        
    print(fname)
    f = open(sys.argv[1] + fname, encoding="utf-8")
    f2 = open(sys.argv[1] + fname+'_ml1.csv', 'w')
    print(">>>>>")
    #Writing the column names...
    #-------------------------------------------------
    f2.write(",".join(["time", "type_id",
        "PCI",
        "DL frequency",
        "UL frequency",
        "DL bandwidth",
        "UL bandwidth",
        "Cell Identity",
        "TAC",
        "Band ID",
        "MCC",
        "MNC",
        "MNC digit",
        ])+'\n')

    l = f.readline()

    #For each dm_log_packet, we will check that whether strings in type_list are shown in it.
    #If yes, type_code will record what types in type_list are shown in the packet.
    #-------------------------------------------------
    type_list = [
        
    ]

    while l:
        if r"<dm_log_packet>" in l:
            # type_code = ["0"] * len(type_list)
            
            soup = BeautifulSoup(l, 'html.parser')
            timestamp = soup.find(key="timestamp").get_text()
            type_id = soup.find(key="type_id").get_text()

            if type_id == "LTE_RRC_Serv_Cell_Info":
                PCI = soup.find(key="Cell ID").get_text()
                DL_f = soup.find(key="Downlink frequency").get_text()
                UL_f = soup.find(key="Uplink frequency").get_text()
                DL_BW = soup.find(key="Downlink bandwidth").get_text()
                UL_BW = soup.find(key="Uplink bandwidth").get_text()
                Cell_identity = soup.find(key="Cell Identity").get_text()
                TAC = soup.find(key="TAC").get_text()
                Band_ID = soup.find(key="Band Indicator").get_text()
                MCC = soup.find(key="MCC").get_text()
                MNC_d = soup.find(key="MNC Digit").get_text()
                MNC = soup.find(key="MNC").get_text()                
                f2.write(",".join([timestamp, type_id, PCI, DL_f, UL_f, DL_BW, UL_BW, Cell_identity, TAC, Band_ID, MCC, MNC, MNC_d] )+'\n')
            else: # 不處理其他資料
                while l and r"</dm_log_packet>" not in l:
                    l = f.readline()

            l = f.readline()
            
            
        else:
            print(l,"Error!")
            break 
            
    f2.close()
    f.close()
