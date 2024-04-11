from .handover import HO
from .signal_strength import SS

# Functions input ordered_HOs and output ordered_HOs with revised ho time align to server time 
def ho_time_to_server_time(ordered_HOs, TS_df, delta):

    i = 0
    ordered_HOs_ = []
    for elements in ordered_HOs:
        if len(elements) == 3:
            Type, ho, mr = elements[0], elements[1], elements[2]
        else:
            Type, ho = elements[0], elements[1]

        while i != len(TS_df)-1:
            diff = (TS_df['cell time'].iloc[i]  - ho.start).total_seconds()
            diff_ = (TS_df['cell time'].iloc[i+1]  - ho.start).total_seconds()
            if abs(diff) < abs(diff_):
                # device time + delta = server time; server time - cell time = server cell delta
                server_cell_delta = TS_df['device time'].iloc[i] + delta - TS_df['cell time'].iloc[i]
                ho_ = HO(start=ho.start+server_cell_delta, end=ho.end+server_cell_delta, others=ho.others, trans=ho.trans)
                if len(elements) == 3:
                    ordered_HOs_.append([Type, ho_, mr])
                else:
                    ordered_HOs_.append([Type, ho_])
                break
            i+=1
    return ordered_HOs_

# Functions input ordered_HOs and output ordered_HOs with revised ho time align to client time 
def ho_time_to_client_time(ordered_HOs, TS_df):

    i = 0
    ordered_HOs_ = []
    for elements in ordered_HOs:
        if len(elements) == 3:
            Type, ho, mr = elements[0], elements[1], elements[2]
        else:
            Type, ho = elements[0], elements[1]

        while i != len(TS_df)-1:
            diff = (TS_df['cell time'].iloc[i]  - ho.start).total_seconds()
            diff_ = (TS_df['cell time'].iloc[i+1]  - ho.start).total_seconds()
            if abs(diff) < abs(diff_):
                # device time - cell time = client cell delta
                client_cell_delta = TS_df['device time'].iloc[i] - TS_df['cell time'].iloc[i]
                ho_ = HO(start=ho.start+client_cell_delta, end=ho.end+client_cell_delta, others=ho.others, trans=ho.trans)
                if len(elements) == 3:
                    ordered_HOs_.append([Type, ho_, mr])
                else:
                    ordered_HOs_.append([Type, ho_])
                break
            i+=1
    return ordered_HOs_

# Functions input ss output ss with revised time align to server time 
def ss_time_to_server_time(Cell, TS_df, delta):
    i = 0
    Cell_ = []
    for ss in Cell:
    
        while i != len(TS_df)-1:
            
            diff = (TS_df['cell time'].iloc[i]  - ss.Timestamp).total_seconds()
            diff_ = (TS_df['cell time'].iloc[i+1]  - ss.Timestamp).total_seconds()
            if abs(diff) < abs(diff_):
                # device time + delta = server time; server time - cell time = server cell delta
                server_cell_delta = TS_df['device time'].iloc[i] + delta - TS_df['cell time'].iloc[i]
                ss_ = SS(PCI=ss.PCI, earfcn=ss.earfcn, RSRP=ss.RSRP, RSRQ=ss.RSRQ, Timestamp=ss.Timestamp+server_cell_delta)
                Cell_.append(ss_)
                break
            i+=1
    return Cell_

# Use the first delta only
def ss_time_to_server_time_way2(Cell, TS_df, delta):
    # Calculate delta for middle data
    if len(Cell) == 0:
        return []
    ss = Cell[-1]
    i = 0
    while i != len(TS_df)-1:
        diff = (TS_df['cell time'].iloc[i]  - ss.Timestamp).total_seconds()
        diff_ = (TS_df['cell time'].iloc[i+1]  - ss.Timestamp).total_seconds()
        if abs(diff) < abs(diff_):
            # device time + delta = server time; server time - cell time = server cell delta
            server_cell_delta = TS_df['device time'].iloc[i] + delta - TS_df['cell time'].iloc[i]
            break
        i+=1

    Cell_ = []
    for ss in Cell:
        ss_ = SS(PCI=ss.PCI, earfcn=ss.earfcn, RSRP=ss.RSRP, RSRQ=ss.RSRQ, Timestamp=ss.Timestamp+server_cell_delta)
        Cell_.append(ss_)
        
    return Cell_