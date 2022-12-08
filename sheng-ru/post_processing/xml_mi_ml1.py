######xml_mi_phy.py#########
#==============instructions==============
######This file requires the txt file which is generated from offline_analysis.py with lte_meas_analyzer and the mi2log file 
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
    f = open(os.path.join(sys.argv[1], fname), encoding="utf-8")
    f2 = open(os.path.join(sys.argv[1], fname+'_ml1.csv') , 'w')
    print("ml1 >>>>>")
    #Writing the column names...
    #-------------------------------------------------
    f2.write(",".join(["time", "type_id",
        "PCI",
        "RSRP(dBm)",
        "RSRQ(dB)",
        "Serving Cell Index",
        "EARFCN",
        "Number of Neighbor Cells",
        "Number of Detected Cells",
        "PCI1",
        "LTE_RSRP1",
        "LTE_RSRQ1"
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

            try:
                PCI = soup.find(key="Serving Physical Cell ID").get_text() ## This is current serving cell PCI.
            except:
                PCI = "-"

            if type_id == 'LTE_PHY_Connected_Mode_Intra_Freq_Meas':
                rsrps = [rsrp.get_text() for rsrp in soup.findAll(key="RSRP(dBm)")]
                rsrqs = [rsrq.get_text() for rsrq in soup.findAll(key="RSRQ(dB)")]
                serving_cell = soup.find(key="Serving Cell Index").get_text()
                earfcn = soup.find(key="E-ARFCN").get_text()
                n_nei_c = soup.find(key="Number of Neighbor Cells").get_text()
                n_det_c = soup.find(key="Number of Detected Cells").get_text()
                PCIs = [pci.get_text() for pci in soup.findAll(key="Physical Cell ID")] ## This is neighbor measured cells PCI.
                if int(n_det_c) != 0:
                    PCIs = PCIs[:-int(n_det_c)]
                A = [[PCIs[i], rsrps[i+1], rsrqs[i+1]] for i in range(len(PCIs))] ## Information of neighbor cell
                A = list(chain.from_iterable(A))
                f2.write(",".join([timestamp, type_id, PCI, rsrps[0], rsrqs[0], serving_cell, earfcn, n_nei_c, n_det_c] + A)+'\n')
            elif type_id == 'LTE_PHY_Connected_Mode_Neighbor_Measurement': # or type_id == 'LTE_PHY_Serv_Cell_Measurement': ## 無法parse暫時忽略
                f2.write(",".join([timestamp, type_id, PCI, '-', '-', '-', '-', '-', '-']  )+'\n')
                pass
            else: # 只處理ml1資料過濾其他type
                while l and r"</dm_log_packet>" not in l:
                    l = f.readline()

            l = f.readline()
            
            
        else:
            print(l,"Error!")
            break 
            
    f2.close()
    f.close()




