# Release note
# 22_0906 ChihYang add new NSA-5g format


"""

This file can transform the device log to a csv file.


Modify the parameter <devicelog> to the target file's name.


"""
import pandas as pd

"""  ↓    Modify devicelog   below     """
devicelog = "./log_2021-8-16-21-40-12" 
f2name = devicelog+".csv"

f2 = open(f2name, "w")
cols = ['Date', "is_tdd","MCC", "MNC", "CID", "PCI","earfcn", "freq_band_ind","UL_bandwidth","DL_bandwidth","TAC","RSRP","RSRQ","RSSI","SINR","CQI","tx_power","srxlev",
    "MCC_5g","MNC_5g","PCI_5g","RSRP_5g","SINR_5g","RSRQ_5g","ARFCN_5g","band_5g","nr_bw","scs" # 22_0906 CY: add new data format
    "mode1","earfcn1","PCI1","RSRQ1","RSRP1",
    "mode2","earfcn2","PCI2","RSRQ2","RSRP2",
    "mode3","earfcn3","PCI3","RSRQ3","RSRP3",
    "mode4","earfcn4","PCI4","RSRQ4","RSRP4",
    "mode5","earfcn5","PCI5","RSRQ5","RSRP5",
    "mode6","earfcn6","PCI6","RSRQ6","RSRP6",
    "mode7","earfcn7","PCI7","RSRQ7","RSRP7",
    "mode8","earfcn8","PCI8","RSRQ8","RSRP8",
    ]
ltenum = 18
nsa5g = 11

earfcn = None
is_5g = False
is_4g = True
filled_5g = False
f2.write(",".join(cols))
with open(f1name) as f1:
    l = f1.readline()
    l2 = []
    l3 = []
    while l:
        l = l.replace('\n', '')
        if "time" in l:
            x = l.find(",")
            ctime = l[x+1:]
#            iif not is_5g:
#                if len(l2) == 1:
#                    l2 += ['0'] * 18
#                l2 += ['0'] * (26 - len(l2))
#            if len(l2):
#                f2.write(",".join(l2+l3)+"\n")
            l3 = []
            l2 = [ctime]
#            pass
#            is_5g = False

        elif "neighbourcell" not in l and '+QENG' in l and 'LTE' in l:
            """
                In LTE mode: 
                +QENG:  "servingcell",<state>,"LTE",<is_tdd>,<MCC>,<
                MNC>,<cellID>,<PCID>,<earfcn>,<freq_band_ind>,<UL_b
                andwidth>,<DL_bandwidth>,<TAC>,<RSRP>,<RSRQ>,<R
                SSI>,<SINR>,<CQI>,<tx_power>,<srxlev>   
                In WCDMA mode: 
                +QENG:  "servingcell",<state>,"WCDMA",<MCC>,<MN
                C>,<LAC>,<cellID>,<uarfcn>,<PSC>,<RAC>,<RSCP>,<eci
                o>,<phych>,<SF>,<slot>,<speech_code>,<comMod>   

                In LTE mode:
                +QENG: "servingcell",<state>,"LTE",<is_tdd>,<MCC>,<MNC>,<cellID>,<PCID>,<earfcn>,<freq_band_ind>,<UL_bandwidth>,<DL_bandwidth>,<TAC>,<RSRP>,<RSRQ>,<RSSI>,<SINR>,<CQI>,
                        0               1      2        3     4     5       6       7       8           9               10              11      12      13      14    15    16      17
                <tx_power>,<srxlev>
                    18        19

                In EN-DC mode:
                    +QENG: "LTE",<is_tdd>,<MCC>,<MNC>,<cellID>,<PCID>,<earfcn>,<freq_band_ind>,
                    <UL_bandwidth>,<DL_bandwidth>,<TAC>,<RSRP>,<RSRQ>,<RSSI>,<SINR>,<CQI>,<tx_power>,<srxlev>
                In EN-DC mode:
                +QENG: "servingcell",<state>
                +QENG: "LTE",       <is_tdd>,<MCC>,<MNC>,<cellID>,<PCID>,<earfcn>,<freq_band_ind>,<UL_bandwidth>,<DL_bandwidth>,<TAC>,<RSRP>,<RSRQ>,<RSSI>,<SINR>,<CQI>,<tx_power>,<srxlev>
                        0           1           2   3       4       5       6           7               8               9       10      11      12      13  14      15      16          17
                +QENG: "NR5G-NSA",  <MCC>,<MNC>,<PCID>,<RSRP>,<SINR>,<RSRQ>,<ARFCN>,<band>,<NR_DL_bandwidth>,<scs>
                        0           1       2       3   4       5       6       7       8       9               10
             """
            l = l.split(",")

            if len(l) == ltenum:
                l2 += l[1:]
                earfcn = l[6]
            else:
                is_4g = True
                l2 += l[3:]
                earfcn = l[8]
        elif "neighbourcell" not in l in l and '+QENG' in l and 'NR5G-NSA' in l:
            """
                "OK":+QENG: "NR5G-NSA",<MCC>,<MNC>,<PCID>,<RSRP>,<SINR>,<RSRQ>,<ARFCN>,<band>
                "FAIL":+QENG: "NR5G-NSA",<MCC>,<MNC>,<RSRP>,<SINR>,<RSRQ>,<ARFCN>,<band>
                            0               1   2       3       4   5       6       7
                22_0906 CY: A06 vesrion FW format
                ok version
                +QENG: "NR5G-NSA",  <MCC>,<MNC>,<PCID>,<RSRP>,<SINR>,<RSRQ>,<ARFCN>,<band>,<NR_DL_bandwidth>,<scs>
                        0           1       2      3      4      5     6       7       8          9            10
                fail
            """
            l = l.split(",")
            is_5g = True
            if (len(l) == 7) or "-32768" in l:
                l2 += l[1:3]
                l2.append("-1")
                l2 += l[3:]
#                l2.append("0")     # why??
            else:
                l2 += l[1:-1]
        elif "neighbourcell" in l and '+QENG' in l:

            """
            In LTE mode:   
            [+QENG:  "neighbourcell  intra",1"LTE",2<earfcn>,3<PCID>,4<
            RSRQ>,5<RSRP>,6<RSSI>,7<SINR>,<srxlev>,<cell_resel_pri
            ority>,<s_non_intra_search>,<thresh_serving_low>,<s_i
            ntra_search> 
            …] 
            [+QENG:  "neighbourcell  inter",1"LTE",2<earfcn>,3<PCID>,4<
            RSRQ>,5<RSRP>,6<RSSI>,7<SINR>,<srxlev>,<cell_resel_pri
            ority>,<threshX_low>,<threshX_high> 
            …] 
            [+QENG:"neighbourcell",1"WCDMA",2<uarfcn>,<cell_resel
            _priority>,<thresh_Xhigh>,<thresh_Xlow>,<PSC>,<RSC
            P><ecno>,<srxlev> 
            …] 
            """
            l = l.replace("\"" , "")
            l = l.split(",")

            if "LTE" in l and earfcn == l[2]:
                l3.append(l[1])
                l3.append(l[2])
                l3.append(l[3])
                l3.append(l[4])
                l3.append(l[5])
            
        elif "time" in l:
            x = l.find(",")
            ctime = l[x+1:]
            if not is_5g:
                if len(l2) == 1:
                    l2 += ['0'] * 18
                l2 += ['0'] * (26 - len(l2))
            if len(l2):
                f2.write(",".join(l2+l3)+"\n")
            l3 = []
            l2 = [ctime]
            pass
            is_5g = False
        elif "+QCAINFO:" in l:
            pass
        l = f1.readline()

f2.close()
