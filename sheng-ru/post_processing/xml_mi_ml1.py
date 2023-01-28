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
    f_out = os.path.join(sys.argv[1], fname[:-4]+'_ml1.csv')
    delete = False
    f2 = open(f_out, 'w')
    print("ml1 >>>>>")
    #Writing the column names...
    #-------------------------------------------------
    columns = ["time", "type_id",
        "PCI",
        "RSRP(dBm)",
        "RSRQ(dB)",
        "Serving Cell Index",
        "EARFCN",
        "Number of Neighbor Cells",
        "Number of Detected Cells"]

    f2.write(",".join(columns)+'\n')

    l = f.readline()

    #For each dm_log_packet, we will check that whether strings in type_list are shown in it.
    #If yes, type_code will record what types in type_list are shown in the packet.
    #-------------------------------------------------
    type_list = [
        
    ]

    max_length = 0
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
                x = len([timestamp, type_id, PCI, rsrps[0], rsrqs[0], serving_cell, earfcn, n_nei_c, n_det_c] + A)
                max_length = x if x > max_length else max_length
                f2.write(",".join([timestamp, type_id, PCI, rsrps[0], rsrqs[0], serving_cell, earfcn, n_nei_c, n_det_c] + A)+'\n')


            else: # 只處理ml1資料過濾其他type
                while l and r"</dm_log_packet>" not in l:
                    l = f.readline()

            l = f.readline()
            
            
        else:
            print(l,"Error!")
            delete = True
            break 
            
    f2.close()
    f.close()

    if delete:
        os.system(f"rm {f_out}")
    else:
        # csv Header process
        with open(f_out, 'r') as csvinput:
            new_f = f_out[:-4]+"_new.csv"
            l = csvinput.readline()
            x = len(l.split(','))
            X = []
            for i in range(int((max_length-x)/3)):
                X += [f"PCI{i+1}",f"RSRP{i+1}",f"RSRQ{i+1}"]
            X = columns+X
            with open(new_f, 'w') as csvoutput:
                csvoutput.write(",".join(X)+'\n')
                l = csvinput.readline()
                while l:
                    csvoutput.write(l)
                    l = csvinput.readline()
        os.system(f"rm {f_out}") # Remove 