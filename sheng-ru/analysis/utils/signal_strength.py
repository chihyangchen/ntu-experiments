import numpy as np
import datetime as dt
import pandas as pd
from collections import namedtuple

SS = namedtuple('SS', ['PCI', 'earfcn', 'RSRP', 'RSRQ', 'Timestamp'], defaults=['','',0,0,None])
def LTE_signal_strength(ml1_file, time_range, cut=True, TZ=False):
    # Read csv with pandas
    ml1_df = pd.read_csv(ml1_file)
    ml1_df['Timestamp'] = pd.to_datetime(ml1_df['Timestamp'])
    if TZ:
        ml1_df['Timestamp'] = ml1_df['Timestamp'] + pd.Timedelta(hours=8)
    ml1_df = ml1_df.astype({'PCI': str, 'EARFCN': str})

    # Read ml1 csv data
    Cells = {}
    PCell = []
    SCell1, SCell2, SCell3 = [], [], []

    hys = dt.timedelta(seconds=5)
    start_time = time_range[0] - hys
    end_time = time_range[1] + hys

    for i in range(len(ml1_df)):

        t = ml1_df['Timestamp'].iloc[i]
        if t < start_time: continue
        elif start_time <= t < end_time: pass
        elif end_time <= t: break

        serv_cell_idx = ml1_df['Serving Cell Index'].iloc[i]
        pci = ml1_df['PCI'].iloc[i]
        earfcn = ml1_df['EARFCN'].iloc[i]
        rsrp = ml1_df['RSRP(dBm)'].iloc[i]
        rsrq = ml1_df['RSRQ(dB)'].iloc[i]

        ss = SS(pci, earfcn, rsrp, rsrq, t)
        
        if serv_cell_idx == 'PCell':
            PCell.append(ss)
        elif serv_cell_idx == '1_SCell':
            SCell1.append(ss)
        elif serv_cell_idx == '2_SCell':
            SCell2.append(ss)
        elif serv_cell_idx == '(MI)Unknown':
            SCell3.append(ss)

        k = pci+' '+earfcn 
        if k in Cells.keys():
            Cells[k].append(ss)
        else:
            Cells[k] = [ss]

        # Cells
        num_neicells = ml1_df['Number of Neighbor Cells'].iloc[i]
        
        try: index = ml1_df.columns.get_loc('PCI1')
        except KeyError: continue

        for j in np.arange(index, index+num_neicells*3,3):
            pci = str(int(ml1_df.iloc[i][j]))
            rsrp = ml1_df.iloc[i][j+1]
            rsrq = ml1_df.iloc[i][j+2]
            ss = SS(pci, earfcn, rsrp, rsrq, t)
            k = pci+' '+earfcn 

            if k in Cells.keys():
                Cells[k].append(ss)
            else:
                Cells[k] = [ss]
    
    return PCell, SCell1, SCell2, SCell3, Cells

def NR_signal_strength(ml1_file, time_range, TZ=False):
    # Read csv with pandas
    ml1_df = pd.read_csv(ml1_file)
    Cells = {}
    PSCell = []
    if len(ml1_df) == 0:
        return PSCell, Cells
    ml1_df['Timestamp'] = pd.to_datetime(ml1_df['Timestamp'])
    if TZ:
        ml1_df['Timestamp'] = ml1_df['Timestamp'] + pd.Timedelta(hours=8)
    ml1_df = ml1_df.astype({'Serving Cell PCI': str, 'Raster ARFCN': str})
    
    hys = dt.timedelta(seconds=5)
    start_time = time_range[0] - hys
    end_time = time_range[1] + hys

    for i in range(len(ml1_df)):
        t = ml1_df['Timestamp'].iloc[i]
        if t < start_time: continue
        elif start_time <= t < end_time: pass
        elif end_time <= t: break

        PSCell_pci = ml1_df['Serving Cell PCI'].iloc[i]
        earfcn = ml1_df['Raster ARFCN'].iloc[i]

        try: index = ml1_df.columns.get_loc('PCI0')
        except KeyError: continue

        # Deal with Cells first        
        for j in np.arange(index, len(ml1_df.columns),3):
            if np.isnan(ml1_df.iloc[i][j]):
                break
            pci = str(int(ml1_df.iloc[i][j]))
            rsrp = ml1_df.iloc[i][j+1]
            rsrq = ml1_df.iloc[i][j+2]
            ss = SS(pci, earfcn, rsrp, rsrq, t)
            k = pci+' '+earfcn 

            if k in Cells.keys():
                Cells[k].append(ss)
            else:
                Cells[k] = [ss]

        # Deal with PSCell
        if PSCell_pci == '65535':
            continue
        ss = Cells[PSCell_pci+' '+earfcn][-1]
        PSCell.append(ss)
        
    
    return PSCell, Cells