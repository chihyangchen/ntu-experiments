#!/usr/bin/python3
### Filename: udp_analysis.py

"""
Analyze packet capture of udp experiments.
Need to convert .pcap into .csv by tshark with script udp_pcap_to_csv.py

若 pcap, ho.csv 檔案為空:
    start_time = '-'
    end_time = '-'
    exp_time = 0

Author: Yuan-Jye Chen
Update: Yuan-Jye Chen 2022/10/09
"""

"""
    Future Development Plan
        (1) Neglect filename start with ".~lock". (e.g., ".~lock.packet_info.csv#", ".~lock.client_pcap_BL_sm05_3210_3211_2022-09-29_16-24-57.csv#")
        (2) Output packet loss statistics and lanency.
        (3) Time synchronization. (preprocessing)
        (4) functionalize
        (5) 對一下 packet loss rate / packet loss number 是否與截圖 summary 相符
        (6) 若一開始就掉封包，建議改成外插法預測！
        (7) focus 在 UE 端狀況，因此 timestamp 應取 expected arrival time (DL) 和 transmit time (UL)，目前都是取 expected arrival time。
        (8) readline of csv 逐行（不要一次 handle 整個 dataframe，因為 payload 太長，RAM 會爆掉），目前先把 rxdf, txdf 分別處理，不要兩個都讀進來才處理（30min-500pps-pcap.csv 還夠用）
    
"""
import os
import sys
import argparse
import csv
import pandas as pd
import datetime as dt
import numpy as np
from pprint import pprint
from tqdm import tqdm
from pytictoc import TicToc
import traceback
from statistics import median
from statistics import mean
from statistics import mode
from statistics import stdev
from scipy import stats
from scipy import signal
import portion as P
import swifter

# ******************************* User Settings *******************************
database = "/home/wmnlab/D/database/"
# date = "2023-01-12"
dates = [
        #  "2023-02-04", 
        #  "2023-02-04#1",
         "2023-02-27",
         ]
devices = sorted([
    # "sm00",
    # "sm01",
    # "sm02",
    # "sm03",
    # "sm04",
    # "sm05",
    # "sm06",
    # "sm07",
    # "sm08",
    "qc00",
    "qc01",
    # "qc02",
    # "qc03",
])
exps = {  # experiment_name: (number_of_experiment_rounds, list_of_experiment_round)
            # If the list is None, it will not list as directories.
            # If the list is empty, it will list all directories in the current directory by default.
            # If the number of experiment times != the length of existing directories of list, it would trigger warning and skip the directory.
    "_Bandswitch": (1, []),
    # "tsync": (2, []),
    # "_Bandlock_Udp_B3_B7_B8_RM500Q": (2, []),
    # "_Bandlock_Udp_all_RM500Q": (2, []),
    # "_tsync": (1, ["#02",]),
    # "_tsync": (1, []),
    # "_Bandlock_Udp": (4, ["#01", "#02", "#03", "#04"]),
    # "_Bandlock_Udp": (4, ["#03", "#04", "#05", "#06"]),
    # "_Bandlock_Udp": (4, []),
    # "_Bandlock_Udp": (6, []),
    # "_Bandlock_Udp_B1_B3":  (6, []),
    # "_Bandlock_Udp_B3_B28": (2, []),
    # "_Bandlock_Udp_B28_B1": (2, []),
    # "_Bandlock_Udp_B1_B3": (4, []),
    # "_Bandlock_Udp_B3_B7": (4, []),
    # "_Bandlock_Udp_B7_B8": (4, []),
    # "_Bandlock_Udp_B8_B1": (4, []),
    # "_Modem_Phone_Comparative_Exeriments": (6, []),
    # "tsync": (1, None),
}

class Payload:
    LENGTH = 250              # (Bytes)
    TAG = "000425d401df5e76"  # 2 71828 3 1415926 (hex)            : 8-bytes
    OFS_TIME = (16, 24)       # epoch time of 'yyyy/mm/dd hh:mm:ss': 4-bytes
    OFS_USEC = (24, 32)       # microsecond (usec)                 : 4-bytes
    OFS_SEQN = (32, 40)       # sequence number (start from 1)     : 4-bytes
class ServerIP:
    PUBLIC = "140.112.20.183"  # 2F    
    PRIVATE = "192.168.1.251"  # 2F
    # PRIVATE = "192.168.1.248"  # 2F previous
    # PUBLIC = "140.112.17.209"  # 3F
    # PRIVATE = "192.168.1.108"  # 3F

# DATA_RATE = 1000e3  # bits-per-second
# PKT_RATE = DATA_RATE / Payload.LENGTH / 8  # packets-per-second
# print("packet_rate (pps):", PKT_RATE, "\n")
# *****************************************************************************

# ****************************** Utils Functions ******************************
def makedir(dirpath, mode=0):  # mode=1: show message; mode=0: hide message
    if os.path.isdir(dirpath):
        if mode:
            print("mkdir: cannot create directory '{}': directory has already existed.".format(dirpath))
        return
    ### recursively make directory
    _temp = []
    while not os.path.isdir(dirpath):
        _temp.append(dirpath)
        dirpath = os.path.dirname(dirpath)
    while _temp:
        dirpath = _temp.pop()
        print("mkdir", dirpath)
        os.mkdir(dirpath)

def epoch_to_utc8(ts):
    """
    Convert an epoch time into a readable format.
    Switch from utc-0 into utc-8.
    
    Args:
        ts (float): timestamp composed of datetimedec + microsecond (e.g., 1644051509.989306)
    Returns:
        (datetime.datetime): a readable timestamp (utc-8)
    """
    return (dt.datetime.utcfromtimestamp(ts) + dt.timedelta(hours=8))

def str_to_datetime(ts):
    """
    Convert a timestamp string in microseconds or milliseconds into datetime.datetime

    Args:
        ts (str): timestamp string (e.g., 2022-09-29 16:24:58.252615)
    Returns:
        (datetime.datetime)
    """
    try:
        ts_datetime = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
    except:
        ts_datetime = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    return ts_datetime

def datetime_to_str(ts):
    """
    Convert a datetime timestamp in microseconds into str

    Args:
        ts (datetime.datetime): datetime timestamp (e.g., datetime.datetime(2022, 9, 29, 16, 24, 58, 252615))
    Returns:
        (str): timestamp string (e.g., 2022-09-29 16:24:58.252615)
    """
    try:
        ts_string = dt.datetime.strftime(ts, "%Y-%m-%d %H:%M:%S.%f")
    except:
        ts_string = dt.datetime.strftime(ts, "%Y-%m-%d %H:%M:%S")
    return ts_string
# *****************************************************************************

# **************************** Auxiliary Functions ****************************
def filter(df, direction, terminal, protocol):
    """
    Filtering the content which are needed.

    Args:
        df (pandas.Dataframe)
        direction (str): "uplink" or "downlink"
        terminal  (str): "server" or "client"
        protocol  (str): "tcp" or "udp"
    Returns:
        df (pandas.Dataframe)
    """
    TRANS = 4
    RECV = 0
    TCP = 6
    UDP = 17

    ### UpLink or DownLink
    if terminal == "client":
        if direction == "uplink":
            # df = df[df["sll.pkttype"] == TRANS]
            df = df[np.in1d(df["sll.pkttype"], TRANS)]
        elif direction == "downlink":
            # df = df[df["sll.pkttype"] == RECV]
            df = df[np.in1d(df["sll.pkttype"], RECV)]
    elif terminal == "server":
        if direction == "downlink":
            # df = df[df["sll.pkttype"] == TRANS]
            df = df[np.in1d(df["sll.pkttype"], TRANS)]
        elif direction == "uplink":
            # df = df[df["sll.pkttype"] == RECV]
            df = df[np.in1d(df["sll.pkttype"], RECV)]

    ### TCP or UDP
    if protocol == "udp":
        # df = df[df["ip.proto"] == UDP]
        df = df[np.in1d(df["ip.proto"], UDP)]
    elif protocol == "tcp":
        # df = df[df["ip.proto"] == TCP]
        df = df[np.in1d(df["ip.proto"], TCP)]
    
    ### iPerf customized packet
    # if protocol == "udp":
    #     df = df[df["udp.payload"].str.contains(Payload.TAG)]  # a safety way but only supporting data generated by modified iPerf
    # elif protocol == "tcp":
    #     df = df[df["tcp.payload"].str.contains(Payload.TAG)]  # a safety way but only supporting data generated by modified iPerf
    # df = df[(df["udp.length"] % Payload.LENGTH == 8) & (df["udp.length"] > Payload.LENGTH)]
    df = df[(np.in1d(df["udp.length"] % Payload.LENGTH, 8)) & (df["udp.length"] > Payload.LENGTH)]
    
    ### Type casting: convert frame.time into datetime
    try:
        df["frame.time"] = pd.to_datetime(df["frame.time"]).dt.tz_localize(None)  # to remove the time zone information while keeping the local time
        # df["frame.time"] = df["frame.time"].apply(lambda x: pd.to_datetime(x).tz_localize(None))  # to remove the time zone information while keeping the local time
        # df["frame.time"] = df["frame.time"].swifter.apply(lambda x: pd.to_datetime(x).tz_localize(None))  # to remove the time zone information while keeping the local time
        # df['frame.time'] = pd.to_datetime(df['frame.time'])
        # df['frame.time'] = df['frame.time'].dt.tz_localize(None)  # to remove the time zone information while keeping the local time
        # with pd.option_context('display.max_rows', None):
        #     print(df['frame.time'])
    except:
        print(traceback.format_exc())
        sys.exit(1)
    
    return df

def parse_packet_info(df, fout, mode=0):
    """
    Parse packet info. | Stage 1
    repackage: transport layer protocol may repackage multiple payload into 1 frame (capture),
                so data.len would be an integer multiple of customized Payload.LENTGH.
    solution. => repkg_num

    Args:
        df (pandas.Dataframe): pcap.csv dataframe
        fout (str): output filepath
        mode (int): 0 means output w/o packet's payload; 1 means output w/ packet's payload.
    Returns:
        df (pandas.Dataframe)
    """
    ### Extract the features which are needed
    # UDP
    df = df[["frame.time", "frame.time_epoch", "udp.length", "data.len", "_ws.col.Protocol", "ip.proto", "ip.src", "ip.dst", "udp.payload"]]
    # TCP
    # df = df[["frame.time", "frame.time_epoch", "tcp.len", "data.len", "_ws.col.Protocol", "ip.proto", ip.src", "ip.dst", "tcp.payload"]]
    
    ### Reset index
    df.reset_index(drop=True, inplace=True)

    ### Add features
    df = pd.DataFrame(df, columns=df.columns.tolist()+["repackage.num", "sequence.number", "payload.time", "payload.time_epoch"])
    df = df.reindex(["frame.time", "frame.time_epoch", "ip.src", "ip.dst", "_ws.col.Protocol", "ip.proto", "udp.length", "data.len", "repackage.num", "sequence.number", "payload.time", "payload.time_epoch", "udp.payload"], axis=1)

    ### Parsing
    for i in tqdm(range(len(df))):
        repkg_num = int(df.loc[i, "udp.length"] // Payload.LENGTH)
        _offset = [s * Payload.LENGTH * 2 for s in list(range(repkg_num))]  # 1-Byte == 2-hex-digits
        payload = df.loc[i, "udp.payload"]  # string-type
        # print(repkg_num)
        _temp = [[], [], []]  # [[seq,], [payload_time,], [payload_time_epoch,]]
        for ofs in _offset:
            try:
                datetimedec = int(payload[ofs + Payload.OFS_TIME[0] : ofs + Payload.OFS_TIME[1]], 16)
                microsec = int(payload[ofs + Payload.OFS_USEC[0] : ofs + Payload.OFS_USEC[1]], 16)
                seq = int(payload[ofs + Payload.OFS_SEQN[0] : ofs + Payload.OFS_SEQN[1]], 16)
            except:
                print(traceback.format_exc())
                # print(df.loc[i-1, "frame.time"])
                # print(df.loc[i-1, "udp.payload"])
                print(df.loc[i, "frame.time"])
                print(payload)
                sys.exit(1)
            payload_time = str(epoch_to_utc8(datetimedec + microsec * 1e-6))
            # print("   ", seq)
            # print("   ", gen_time)
            _temp[0].append(str(seq))
            _temp[1].append(payload_time)
            _temp[2].append(str(datetimedec + microsec * 1e-6))
        df.at[i, "repackage.num"] = str(round(repkg_num))
        df.at[i, "sequence.number"] = '@'.join(_temp[0])
        df.at[i, "payload.time"] = '@'.join(_temp[1])
        df.at[i, "payload.time_epoch"] = '@'.join(_temp[2])
    
    ### Rename some features
    df.rename(columns = {"frame.time":"Timestamp", "frame.time_epoch":"Timestamp_epoch"}, inplace=True)

    ### Output results
    print("output >>>", fout)
    if not mode:  # drop packet's payload
        df = df[df.columns.tolist()[:-1]]
    df.to_csv(fout, index=False)
    return df

def parse_brief_info(df, fout):
    """
    Parse packet brief info. | Stage 2
    duplicate: some packets with the same payload data (same payload generating time & sequence number) arrives at different time.
                since UDP should not do retransmission, only the first arriving packet would be taken into account.
    # solution. => seq_set()

    Args:
        df (pandas.Dataframe): pkt_info.csv dataframe
        fout (str): output filepath
    Returns:
        df (pandas.Dataframe)
    """
    ### Type casting
    # df["Timestamp"] = df["Timestamp"].apply(lambda x: pd.to_datetime(x))
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    ### Parsing
    timestamp_list = []
    seq_set = set()
    for i in tqdm(range(len(df))):
        ftime = df.at[i, "Timestamp"]
        ftime_epoch = df.at[i, "Timestamp_epoch"]
        _seq = [int(s) for s in df.at[i, "sequence.number"].split('@')]
        _ptime = [str_to_datetime(s) for s in df.at[i, "payload.time"].split('@')]
        _ptime_epoch = [float(s) for s in df.at[i, "payload.time_epoch"].split('@')]
        repkg_num = df.at[i, "repackage.num"]
        for seq, ptime, ptime_epoch in zip(_seq, _ptime, _ptime_epoch):
            if seq not in seq_set:
                timestamp_list.append([seq, repkg_num, ftime, ftime_epoch, ptime, ptime_epoch])
                seq_set.add(seq)

    ### Consider if there are out-of-order packets
    timestamp_list = sorted(timestamp_list, key = lambda v : v[0])

    ### Output the results
    print("output >>>", fout)
    with open(fout, 'w', newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["sequence.number", "repackage.num", "Timestamp", "Timestamp_epoch", "payload.time", "payload.time_epoch"])
        writer.writerows(timestamp_list)
    return df
# *****************************************************************************


if __name__ == "__main__":
    def fgetter(direction, terminal):
        if direction == "uplink" and terminal == "client":
            tags = ("client_pcap_BL", "client_pcap_UL")
        elif direction == "downlink" and terminal == "client":
            tags = ("client_pcap_BL", "client_pcap_DL")
        elif direction == "uplink" and terminal == "server":
            tags = ("server_pcap_BL", "server_pcap_UL")
        elif direction == "downlink" and terminal == "server":
            tags = ("server_pcap_BL", "server_pcap_DL")
        for filename in filenames:
            if filename.startswith(tags) and filename.endswith(".csv"):
                print(">>>>>", os.path.join(source_dir, filename))
                if "BL" in filename:
                    return os.path.join(source_dir, filename), 0
                else:
                    return os.path.join(source_dir, filename), 1
        print("No candidate file.")
        return None, 1

    def main():
        ### detailed information for each udp packet's frame
        # udp_uplk_client_pkt_info   # udp ultx detailed info
        # udp_uplk_server_pkt_info   # udp ulrx detailed info
        # udp_dnlk_server_pkt_info   # udp dltx detailed info
        # udp_dnlk_client_pkt_info   # udp dlrx detailed info

        ### brief information for each udp packet
        # udp_uplk_client_pkt_brief  # udp ultx brief info
        # udp_uplk_server_pkt_brief  # udp ulrx brief info
        # udp_dnlk_server_pkt_brief  # udp dltx brief info
        # udp_dnlk_client_pkt_brief  # udp dlrx brief info

        ### dirpath
        # source_dir
        # target_dir

        ### parse detailed information & brief information for each packet
        
        do = 1
        ## client_pcap_BL or client_pcap_UL
        t1 = TicToc()  # create instance of class
        t1.tic()       # Start timer
        t2 = TicToc()
        t2.tic()
        if do:
            filepath, do = fgetter("uplink", "client")
            df = pd.read_csv(filepath, sep='@')
        t2.toc()
        t2 = TicToc()
        t2.tic()
        df_ultx = filter(df.copy(), "uplink", "client", "udp")
        t2.toc()
        t2 = TicToc()
        t2.tic()
        df_ultx = parse_packet_info(df_ultx, os.path.join(target_dir, "udp_uplk_client_pkt_info.csv"))
        t2.toc()
        t2 = TicToc()
        t2.tic()
        df_ultx = parse_brief_info(df_ultx, os.path.join(target_dir, "udp_uplk_client_pkt_brief.csv"))
        t2.toc()
        os.system(f'rm {os.path.join(target_dir, "udp_uplk_client_pkt_info.csv")}') # Remove
        t1.toc()  # Time elapsed since t1.tic()
        
        # do = 1
        ## client_pcap_BL or client_pcap_DL
        t1 = TicToc()  # create instance of class
        t1.tic()       # Start timer
        if do:
            filepath, do = fgetter("downlink", "client")
            df = pd.read_csv(filepath, sep='@')
        df_dlrx = filter(df, "downlink", "client", "udp")
        df_dlrx = parse_packet_info(df_dlrx, os.path.join(target_dir, "udp_dnlk_client_pkt_info.csv"))
        df_dlrx = parse_brief_info(df_dlrx, os.path.join(target_dir, "udp_dnlk_client_pkt_brief.csv"))
        os.system(f'rm {os.path.join(target_dir, "udp_dnlk_client_pkt_info.csv")}') # Remove
        t1.toc()  # Time elapsed since t1.tic()

        do = 1
        ## server_pcap_BL or server_pcap_UL
        t1 = TicToc()  # create instance of class
        t1.tic()       # Start timer
        if do:
            filepath, do = fgetter("uplink", "server")
            df = pd.read_csv(filepath, sep='@')
        df_ulrx = filter(df.copy(), "uplink", "server", "udp")
        df_ulrx = parse_packet_info(df_ulrx, os.path.join(target_dir, "udp_uplk_server_pkt_info.csv"))
        df_ulrx = parse_brief_info(df_ulrx, os.path.join(target_dir, "udp_uplk_server_pkt_brief.csv"))
        os.system(f'rm {os.path.join(target_dir, "udp_uplk_server_pkt_info.csv")}') # Remove
        t1.toc()  # Time elapsed since t1.tic()
        
        # do = 1
        ## server_pcap_BL or server_pcap_DL
        t1 = TicToc()  # create instance of class
        t1.tic()       # Start timer
        if do:
            filepath, do = fgetter("downlink", "server")
            df = pd.read_csv(filepath, sep='@')
        df_dltx = filter(df, "downlink", "server", "udp")
        df_dltx = parse_packet_info(df_dltx, os.path.join(target_dir, "udp_dnlk_server_pkt_info.csv"))
        df_dltx = parse_brief_info(df_dltx, os.path.join(target_dir, "udp_dnlk_server_pkt_brief.csv"))
        os.system(f'rm {os.path.join(target_dir, "udp_dnlk_server_pkt_info.csv")}') # Remove
        t1.toc()  # Time elapsed since t1.tic()
        print()
        return

    # ******************************* Check Files *********************************
    for date in dates:
        for expr, (times, traces) in exps.items():
            print(os.path.join(database, date, expr))
            for dev in devices:
                if not os.path.isdir(os.path.join(database, date, expr, dev)):
                    print("|___ {} does not exist.".format(os.path.join(database, date, expr, dev)))
                    continue
                
                print("|___", os.path.join(database, date, expr, dev))
                if traces == None:
                    # print(os.path.join(database, date, expr, dev))
                    continue
                elif len(traces) == 0:
                    traces = sorted(os.listdir(os.path.join(database, date, expr, dev)))
                
                print("|    ", times)
                traces = [trace for trace in traces if os.path.isdir(os.path.join(database, date, expr, dev, trace))]
                if len(traces) != times:
                    print("***************************************************************************************")
                    print("Warning: the number of traces does not match the specified number of experiment times.")
                    print("***************************************************************************************")
                for trace in traces:
                    print("|    |___", os.path.join(database, date, expr, dev, trace))
            print()
    # *****************************************************************************

    # ******************************** Processing *********************************
    t = TicToc()  # create instance of class
    t.tic()       # Start timer
    for date in dates:
        for expr, (times, traces) in exps.items():
            for dev in devices:
                if not os.path.isdir(os.path.join(database, date, expr, dev)):
                    print("{} does not exist.\n".format(os.path.join(database, date, expr, dev)))
                    continue

                if traces == None:
                    print("------------------------------------------")
                    print(date, expr, dev)
                    print("------------------------------------------")
                    source_dir = os.path.join(database, date, expr, dev)
                    target_dir = os.path.join(database, date, expr, dev)
                    makedir(target_dir)
                    traces = sorted(os.listdir(os.path.join(database, date, expr, dev)))
                    # filenames = os.listdir(source_dir)
                    # main()
                    # continue
                elif len(traces) == 0:
                    traces = sorted(os.listdir(os.path.join(database, date, expr, dev)))
                
                traces = [trace for trace in traces if os.path.isdir(os.path.join(database, date, expr, dev, trace))]
                for trace in traces:
                    print("------------------------------------------")
                    print(date, expr, dev, trace)
                    print("------------------------------------------")
                    source_dir = os.path.join(database, date, expr, dev, trace, "middle")
                    target_dir = os.path.join(database, date, expr, dev, trace, "middle")
                    if expr == "tsync":
                        source_dir = os.path.join(database, date, expr, dev, trace)
                        target_dir = os.path.join(database, date, expr, dev, trace)
                    makedir(target_dir)
                    filenames = os.listdir(source_dir)
                    main()
    t.toc()  # Time elapsed since t.tic()
    # *****************************************************************************
