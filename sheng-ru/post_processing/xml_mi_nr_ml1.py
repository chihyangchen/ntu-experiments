######xml_mi_nr_phy.py#########
#==============instructions==============#
######This file requires the txt file which is generated from offline_analysis.py enabled "5G_NR_ML1_Searcher_Measurement_Database_Update_Ext"  
######The rows shows the information of each diag mode packets (dm_log_packet) from Mobile Insight 
######The columns are indicators about whether a packet has the type of the message

from bs4 import BeautifulSoup
import sys
import os


dirname = sys.argv[1]

filenames = os.listdir(dirname)

for fname in filenames:
    if fname[-4:] != '.txt':
        continue
        
    print(fname)
    f = open(os.path.join(sys.argv[1], fname), encoding="utf-8")
    f_out = os.path.join(sys.argv[1], fname[:-4]+'_nr_ml1.csv')
    delete = False
    f2 = open(f_out , 'w')
    print("nr_ml1 >>>>>")
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

    max_length = 0
    while l:
        if r"<dm_log_packet>" in l:
            soup = BeautifulSoup(l, 'html.parser')
            timestamp = soup.find(key="timestamp").get_text()
            type_id = soup.find(key="type_id").get_text()

            if type_id == '5G_NR_ML1_Searcher_Measurement_Database_Update_Ext':
                arfcn = soup.find(key="Raster ARFCN").get_text()
                num_cells = soup.find(key="Num Cells").get_text()
                serving_cell_idex = soup.find(key="Serving Cell Index").get_text()
                serving_cell_pci = soup.find(key="Serving Cell PCI").get_text()
                pcis = [pci.get_text() for pci in soup.findAll(key="PCI")]
                rsrps = [rsrp.get_text() for rsrp in soup.findAll(key="Cell Quality Rsrp")]
                rsrqs = [rsrq.get_text() for rsrq in soup.findAll(key="Cell Quality Rsrq")]

                A = []
                for i in range(int(num_cells)):    
                    A.append(pcis[i])
                    A.append(rsrps[i])
                    A.append(rsrqs[i])

                x = len([timestamp, type_id, arfcn, num_cells, serving_cell_idex, serving_cell_pci] + A)
                max_length = x if x > max_length else max_length
                f2.write(",".join([timestamp, type_id, arfcn, num_cells, serving_cell_idex, serving_cell_pci] + A)+'\n')
            
            else: # 只處理nr_ml1資料過濾其他type
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
                X += [f"PCI{i}",f"RSRP{i}",f"RSRQ{i}"]
            X = columns+X
            with open(new_f, 'w') as csvoutput:
                csvoutput.write(",".join(X)+'\n')
                l = csvinput.readline()
                while l:
                    csvoutput.write(l)
                    l = csvinput.readline()
        os.system(f"rm {f_out}") # Remove 