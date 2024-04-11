import numpy as np
import pandas as pd
import datetime as dt
from collections import namedtuple
from .handover import parse_mi_ho

LOSS_PKT = namedtuple('LOSS_PKT',['timestamp', 'seq', 'cause', 'trans', 'trans_time', 'others'], defaults=['', 0, [], [], [], []])
EXCL_PKT = namedtuple('EXCL_PKT',['timestamp', 'seq', 'cause', 'trans', 'trans_time', 'others'], defaults=['', 0, [], [], [], []])
def loss_excl_cause(loss_lat_file_path, rrc_file_path):

    loss_lat_df = pd.read_csv(loss_lat_file_path)
    total_pkg_num = len(loss_lat_df)

    loss_cond = loss_lat_df['lost'] == True
    loss_packets = loss_lat_df[loss_cond]
    loss_packets = loss_packets.reset_index(drop=True)
    loss_packets['Timestamp'] = pd.to_datetime(loss_packets['Timestamp'])

    exc_lat = 0.1
    excl_cond = (loss_cond==False) & (loss_lat_df['latency'] > exc_lat)
    excl_packets = loss_lat_df[excl_cond]
    excl_packets = excl_packets.reset_index(drop=True)
    excl_packets['Timestamp'] = pd.to_datetime(excl_packets['Timestamp'])

    HO_dict = parse_mi_ho(rrc_file_path)
    events = ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB', 'SN_setup', 
              'SN_Rel', 'SN_HO', 'RLF_II', 'RLF_III', 'SCG_RLF',
              'Conn_Req']
    slots = [dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1),
             dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=2), dt.timedelta(seconds=2), dt.timedelta(seconds=2),
             dt.timedelta(seconds=1)]
    
    LOSS_PKTs = []

    for i in range(len(loss_packets)):

        loss_packet = loss_packets.iloc[i]
        loss_packet_timestamp = loss_packet['Timestamp']
        seq = loss_packet['seq']
        
        cause = []
        trans = []
        others = []
        trans_time = []

        for HO_type, slot in zip(events, slots):
            
            HOs = HO_dict[HO_type]  

            for h in HOs:
                
                if h.start - slot < loss_packet_timestamp < h.start:
                    cause.append(f'Before {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append(h.start)
                    others.append(h.others)
                elif (h.end is not None) and (h.start < loss_packet_timestamp < h.end):
                    cause.append(f'During {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append((h.start, h.end))
                    others.append(h.others)
                elif (h.end is not None) and (h.end < loss_packet_timestamp < h.end + slot):
                    cause.append(f'After {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append(h.end)
                    others.append(h.others)

        LOSS_PKTs.append(LOSS_PKT(timestamp=loss_packet_timestamp, seq=seq, cause=cause, others=others))
                
    events = ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB', 'SN_setup', 
              'SN_Rel', 'SN_HO', 'RLF_II', 'RLF_III', 'SCG_RLF',
              'Conn_Req']
    slots = [dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1),
             dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=2), dt.timedelta(seconds=2), dt.timedelta(seconds=1),
             dt.timedelta(seconds=1)]
    
    EXCL_PKTs = []

    for i in range(len(excl_packets)):

        excl_packet = excl_packets.iloc[i]
        excl_packet_timestamp = excl_packet['Timestamp']
        seq = excl_packet['seq']

        cause = []
        trans = []
        trans_time = []
        others = []

        for HO_type, slot in zip(events, slots):
            
            HOs = HO_dict[HO_type]   
            for h in HOs:
                
                if h.start - slot < excl_packet_timestamp < h.start:
                    cause.append(f'Before {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append(h.start)
                    others.append(h.others)
                elif (h.end is not None) and (h.start < excl_packet_timestamp < h.end):
                    cause.append(f'During {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append((h.start, h.end))
                    others.append(h.others)
                elif (h.end is not None) and (h.end < excl_packet_timestamp < h.end + slot):
                    cause.append(f'After {HO_type}') 
                    trans.append(h.trans)
                    trans_time.append(h.end)
                    others.append(h.others)

        EXCL_PKTs.append(EXCL_PKT(timestamp=excl_packet_timestamp, seq=seq, cause=cause, trans=trans, trans_time=trans_time, others=others))
    
    print(f'loss rate: {len(LOSS_PKTs)/total_pkg_num}; excl rate: {len(EXCL_PKTs)/total_pkg_num}')
    return LOSS_PKTs, EXCL_PKTs

LOSS_PKT_DUAL = namedtuple('LOSS_PKT_DUAL',
                            ['timestamp1', 'timestamp2', 'seq', 'cause1', 'cause2', 'trans1', 'trans2', 'others1', 'others2','trans1_time', 'trans2_time'], 
                            defaults=['', '', 0, [], [], [], [], [], [], [], []])
EXCL_PKT_DUAL = namedtuple('EXCL_PKT_DUAL',
                            ['timestamp1', 'timestamp2', 'seq', 'cause1', 'cause2', 'trans1', 'trans2', 'others1', 'others2','trans1_time', 'trans2_time'], 
                            defaults=['', '', 0, [], [], [], [], [], [], [], []])
def loss_excl_cause_dual(loss_lat_file_path1, loss_lat_file_path2, rrc_file_path1, rrc_file_path2):

    df1 = pd.read_csv(loss_lat_file_path1)
    df2 = pd.read_csv(loss_lat_file_path2)

    start_seq = df1['seq'].iloc[0] if df1['seq'].iloc[0] >=  df2['seq'].iloc[0] else df2['seq'].iloc[0]
    end_seq = df1['seq'].iloc[-1] if df1['seq'].iloc[-1] <=  df2['seq'].iloc[-1] else df2['seq'].iloc[-1]
    total_pkg_num = end_seq - start_seq + 1

    cond1 = (df1['seq'] >= start_seq) & (df1['seq'] <= end_seq)
    df1 = df1[cond1]
    df1 = df1.reset_index(drop=True)
    cond2 = (df2['seq'] >= start_seq) & (df2['seq'] <= end_seq)
    df2 = df2[cond2]
    df2 = df2.reset_index(drop=True)

    # Loss calculate for dual radios redundant packets.
    loss_cond = (df1['lost'] == True) & (df2['lost'] == True)
    
    loss_packets1 = df1[loss_cond]
    loss_packets1 = loss_packets1.reset_index(drop=True)
    loss_packets1['Timestamp'] = pd.to_datetime(loss_packets1['Timestamp'])

    loss_packets2 = df2[loss_cond]
    loss_packets2 = loss_packets2.reset_index(drop=True)
    loss_packets2['Timestamp'] = pd.to_datetime(loss_packets2['Timestamp'])

    # Excexxive latency calculate for dual radios redundant packets.
    exc_lat = 0.1 
    excl_cond1 = (loss_cond==False) & (df1['latency'] > exc_lat)
    excl_cond2 = (loss_cond==False) & (df2['latency'] > exc_lat)
    excl_cond = (excl_cond1 == True) & (excl_cond2 == True)
    
    excl_packets1 = df1[excl_cond]
    excl_packets1 = excl_packets1.reset_index(drop=True)
    excl_packets1['Timestamp'] = pd.to_datetime(excl_packets1['Timestamp'])

    excl_packets2 = df2[excl_cond]
    excl_packets2 = excl_packets2.reset_index(drop=True)
    excl_packets2['Timestamp'] = pd.to_datetime(excl_packets2['Timestamp'])

    HO_dict1 = parse_mi_ho(rrc_file_path1)
    HO_dict2 = parse_mi_ho(rrc_file_path2)
    
    events = ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB', 'SN_setup', 
              'SN_Rel', 'SN_HO', 'RLF_II', 'RLF_III', 'SCG_RLF',
              'Conn_Req']
    slots = [dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1),
             dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=2), dt.timedelta(seconds=2), dt.timedelta(seconds=2),
             dt.timedelta(seconds=1)]

    LOSS_PKT_DUALs = []

    for i in range(len(loss_packets1)):

        loss_packet1 = loss_packets1.iloc[i]
        loss_packet1_timestamp = loss_packet1['Timestamp']

        loss_packet2 = loss_packets2.iloc[i]
        loss_packet2_timestamp = loss_packet2['Timestamp']

        seq = loss_packet1['seq']
        
        cause1, cause2 = [], []
        trans1, trans2 = [], []
        others1, others2 = [], []
        trans1_time, trans2_time = [], []

        for HO_type, slot in zip(events, slots):
            
            HOs1 = HO_dict1[HO_type]
            HOs2 = HO_dict2[HO_type]   

            for h in HOs1:
                
                if h.start - slot < loss_packet1_timestamp < h.start:
                    cause1.append(f'Before {HO_type}') 
                    trans1.append(h.trans)
                    trans1_time.append(h.start)
                    others1.append(h.others)

                elif (h.end is not None) and (h.start < loss_packet1_timestamp < h.end):
                    cause1.append(f'During {HO_type}')
                    trans1.append(h.trans)
                    trans1_time.append((h.start, h.end))
                    others1.append(h.others)

                elif (h.end is not None) and (h.end < loss_packet1_timestamp < h.end + slot):
                    cause1.append(f'After {HO_type}')
                    trans1.append(h.trans)
                    trans1_time.append(h.end)
                    others1.append(h.others)
            
            for h in HOs2:
                
                if h.start - slot < loss_packet2_timestamp < h.start:
                    cause2.append(f'Before {HO_type}') 
                    trans2.append(h.trans)
                    trans2_time.append(h.start)
                    others2.append(h.others)

                elif (h.end is not None) and (h.start < loss_packet2_timestamp < h.end):
                    cause2.append(f'During {HO_type}')
                    trans2.append(h.trans)
                    trans2_time.append((h.start, h.end))
                    others2.append(h.others)

                elif (h.end is not None) and (h.end < loss_packet2_timestamp < h.end + slot):
                    cause2.append(f'After {HO_type}')
                    trans2.append(h.trans)
                    trans2_time.append(h.end)
                    others2.append(h.others)
    
        LOSS_PKT_DUALs.append(LOSS_PKT_DUAL(timestamp1=loss_packet1_timestamp, timestamp2=loss_packet2_timestamp, seq=seq, 
        cause1=cause1, cause2=cause2, trans1=trans1, trans2=trans2, others1=others1, others2=others2, trans1_time=trans1_time, trans2_time=trans2_time))
                
    slot = dt.timedelta(seconds=2)

    events = ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB', 'SN_setup', 
              'SN_Rel', 'SN_HO', 'RLF_II', 'RLF_III', 'SCG_RLF',
              'Conn_Req']
    slots = [dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=1),
             dt.timedelta(seconds=1), dt.timedelta(seconds=1), dt.timedelta(seconds=2), dt.timedelta(seconds=2), dt.timedelta(seconds=2),
             dt.timedelta(seconds=1)]
    
    
    EXCL_PKT_DUALs = []

    for i in range(len(excl_packets1)):

        excl_packet1 = excl_packets1.iloc[i]
        excl_packet1_timestamp = excl_packet1['Timestamp']
        excl_packet2 = excl_packets2.iloc[i]
        excl_packet2_timestamp = excl_packet2['Timestamp']

        seq = excl_packet1['seq']

        cause1, cause2 = [], []
        trans1, trans2 = [], []
        others1, others2 = [], []
        trans1_time, trans2_time = [], []

        for HO_type, slot in zip(events, slots):
            
            HOs1 = HO_dict1[HO_type]
            HOs2 = HO_dict2[HO_type]

            for h in HOs1:
                
                if h.start - slot < excl_packet1_timestamp < h.start:
                    cause1.append(f'Before {HO_type}') 
                    trans1.append(h.trans)
                    trans1_time.append(h.start)
                    others1.append(h.others)

                elif (h.end is not None) and (h.start < excl_packet1_timestamp < h.end):
                    cause1.append(f'During {HO_type}')
                    trans1.append(h.trans)
                    trans1_time.append((h.start, h.end))
                    others1.append(h.others)

                elif (h.end is not None) and (h.end < excl_packet1_timestamp < h.end + slot):
                    cause1.append(f'After {HO_type}')
                    trans1.append(h.trans)
                    trans1_time.append(h.end)
                    others1.append(h.others)

            for h in HOs2:
                
                if h.start - slot < excl_packet2_timestamp < h.start:
                    cause2.append(f'Before {HO_type}') 
                    trans2.append(h.trans)
                    trans2_time.append(h.start)
                    others2.append(h.others)

                elif (h.end is not None) and (h.start < excl_packet2_timestamp < h.end):
                    cause2.append(f'During {HO_type}')
                    trans2.append(h.trans)
                    trans2_time.append((h.start, h.end))
                    others2.append(h.others)

                elif (h.end is not None) and (h.end < excl_packet2_timestamp < h.end + slot):
                    cause2.append(f'After {HO_type}')
                    trans2.append(h.trans)                   
                    trans2_time.append(h.end)
                    others2.append(h.others)

        EXCL_PKT_DUALs.append(EXCL_PKT_DUAL(timestamp1=excl_packet1_timestamp, timestamp2=excl_packet2_timestamp, seq=seq, 
        cause1=cause1, cause2=cause2, trans1=trans1, trans2=trans2, others1=others1, others2=others2, trans1_time=trans1_time, trans2_time=trans2_time))

    print(f'dual loss rate: {len(LOSS_PKT_DUALs)/total_pkg_num}; dual excl rate: {len(EXCL_PKT_DUALs)/total_pkg_num}')
    return LOSS_PKT_DUALs, EXCL_PKT_DUALs

PKG = namedtuple('PKG',['Timestamp','seq','latency'],defaults=[None,0,np.nan])
def accumulate_packet(file,time_range):

    L = []
    df = pd.read_csv(file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    hys = dt.timedelta(seconds=0.2)
    start_time = time_range[0] - hys
    end_time = time_range[1] + hys

    for i in range(len(df)):
        
        t = df['Timestamp'].iloc[i]
        if t < start_time: continue
        elif start_time <= t < end_time: pass
        elif end_time <= t: break

        if df['lost'].iloc[i]: continue
        
        seq = df['seq'].iloc[i]
        lat = df['latency'].iloc[i]
        
        L.append(PKG(t,seq,lat))

    return L
