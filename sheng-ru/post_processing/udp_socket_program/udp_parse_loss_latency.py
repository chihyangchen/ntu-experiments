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
import math
import random

# ******************************* User Settings *******************************
database = "/home/wmnlab/D/database/"
# date = "2022-12-26"
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
    # "_Bandlock_Udp_B3_B7_B8_RM500Q": (2, []),
    # "_Bandlock_Udp_all_RM500Q": (2, []),
    # "tsync": (1, None),
    # "_Bandlock_Udp": (4, ["#01", "#02", "#03", "#04"]),
    # "_Bandlock_Udp": (4, ["#03", "#04", "#05", "#06"]),
    # "_Bandlock_Udp": (4, []),
    # "_Bandlock_Udp": (6, []),
    # "_Bandlock_Udp_B1_B3":  (1, ["#01"]),
    # "_Bandlock_Udp_B1_B3":  (6, []),
    # "_Bandlock_Udp_B3_B28": (2, []),
    # "_Bandlock_Udp_B28_B1": (2, []),
    # "_Bandlock_Udp_B1_B3": (4, []),
    # "_Bandlock_Udp_B3_B7": (4, []),
    # "_Bandlock_Udp_B7_B8": (4, []),
    # "_Bandlock_Udp_B8_B1": (4, []),
    # "_Modem_Phone_Comparative_Exeriments": (6, []),
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

DATA_RATE = 1000e3  # bits-per-second
PKT_RATE = DATA_RATE / Payload.LENGTH / 8  # packets-per-second
print("packet_rate (pps):", PKT_RATE, "\n")
# *****************************************************************************

# --------------------- Global Variables ---------------------
INF = 2147483647

# --------------------- Util Functions ---------------------
def makedir(dirpath, mode=0):  # mode=1: show message, mode=0: hide message
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

def error_handling(err_handle):
    """
    Print the error messages during the process.
    
    Args:
        err_handle (str-tuple): (input_filename, output_filename, error_messages : traceback.format_exc())
    Returns:
        (bool): check if the error_messages occurs, i.e., whether it is None.
    """
    if err_handle[2]:
        print()
        print("**************************************************")
        print("File decoding from '{}' into '{}' was interrupted.".format(err_handle[0], err_handle[1]))
        print()
        print(err_handle[2])
        return True
    return False

def to_utc8(ts):
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
        ts_datetime = dt.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
    except:
        ts_datetime = dt.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
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
        ts_string = dt.datetime.strftime(ts, '%Y-%m-%d %H:%M:%S.%f')
    except:
        ts_string = dt.datetime.strftime(ts, '%Y-%m-%d %H:%M:%S')
    return ts_string

def get_loss(txdf, rxdf):
    rxdf['Timestamp'] = pd.to_datetime(rxdf['Timestamp'])  # arrival.time
    rxdf['payload.time'] = pd.to_datetime(rxdf['payload.time'])  # payload.time

    timestamp_list = list(map(list, zip(rxdf['sequence.number'].astype(int).array, rxdf['Timestamp_epoch'].astype(float).array)))
    timestamp_store = None
    loss_timestamp_list = []
    count = 0  # to count the total number of packet losses
    # _eseq = 1  # next expected sequence number
    _eseq = timestamp_list[0][0] # next expected sequence number
    for i in tqdm(range(len(rxdf))):
        timestamp = timestamp_list[i]
        if timestamp[0] == _eseq:
            ### received packet's sequence number as expected
            pass
        else:
            ### packet losses occur
            ### 可處理連續掉 N 個封包的狀況
            ### timestamp_store: 前一刻收到的封包
            ### timestamp: 此時此刻收到的封包
            ### _eseq 為預期收到的封包 sequence number (前一刻收到的 seq number + 1)
            ### rxdf.loc[i, 'sequence.number'] 為此時此刻收到的封包 seq
            ### rxdf.loc[i, 'sequence.number']-pointer+2 == 遺漏的封包數+2 (頭+尾)，因此要去頭去尾才是實際遺漏的封包
            n = timestamp[0] - _eseq + 2
            # if timestamp_store == None:
            #     ### if the first-N packets lost, we cannot predict the loss timestamp, so we only record their sequemce number.
            #     loss_linspace = np.linspace([0, timestamp[1] - (n-1) / PKT_RATE], timestamp, n)
            # else:
            #     loss_linspace = np.linspace(timestamp_store, timestamp, n)
            loss_linspace = np.linspace(timestamp_store, timestamp, n)
            loss_linspace = loss_linspace[1:-1]  # 去頭去尾
            for item in loss_linspace:
                count += 1
                loss_time = [round(item[0]), to_utc8(item[1]), item[1]]  # (expected) arrival timestamp
                loss_timestamp_list.append(loss_time)
        # Update information
        timestamp_store = timestamp
        _eseq = timestamp[0] + 1
    
    ### add payload, transmit timestamp
    tx_ts_arr = list(zip(txdf['sequence.number'].array, txdf['payload.time'].array, txdf['payload.time_epoch'].array, txdf['Timestamp'].array, txdf['Timestamp_epoch'].array))
    j = 0
    N = len(loss_timestamp_list)
    for i in tqdm(range(len(tx_ts_arr))):
        if N == 0:
            break
        if tx_ts_arr[i][0] == loss_timestamp_list[j][0]:
            loss_timestamp_list[j].append(tx_ts_arr[i][1])
            loss_timestamp_list[j].append(tx_ts_arr[i][2])
            loss_timestamp_list[j].append(tx_ts_arr[i][3])
            loss_timestamp_list[j].append(tx_ts_arr[i][4])
            j += 1
            if j == N:
                break
    ### 因為是由 Client 端主動開始和結束實驗，且程式邏輯為: 開 Tcpdump -> 開 iperf -> 關 Tcpdump -> 關 iperf
    ### 因此 Uplink TX 的 MAX_SEQ 會比 RX 小，Downlink TX 的 MAX_SEQ 會比 RX 大。
    loss_timestamp_list = [item for item in loss_timestamp_list if len(item) == 7]
    # pprint(loss_timestamp_list)
    
    # N = len(loss_timestamp_list)
    loss_timestamps = list(map(list, zip(*loss_timestamp_list)))
    df = pd.DataFrame.from_dict(
        {
            "sequence.number": loss_timestamps[0],
            "Timestamp": loss_timestamps[3],  # payload.time
            "Timestamp_epoch": loss_timestamps[4],  # payload.time_epoch
            "lost": [True] * N,
            "latency": [INF] * N,
            "transmit.time": loss_timestamps[5],
            "transmit.time_epoch": loss_timestamps[6],
            "arrival.time": loss_timestamps[1],
            "arrival.time_epoch": loss_timestamps[2],
        }
    )
    # print(df)
    return df

def get_match(txdf, rxdf):
    ### add transmitted timestamp
    
    # # print(len(txdf))
    # # print(len(rxdf))
    # j = 0
    # N = len(txdf)
    # M = len(rxdf)
    # rxdf = rxdf.reindex(rxdf.columns.tolist() + ['transmit.time', 'transmit.time_epoch'], axis=1)
    # for i in tqdm(range(len(rxdf))):
    #     while j != N and txdf.at[j, 'sequence.number'] != rxdf.at[i, 'sequence.number']:
    #         j += 1
    #     if j != N:
    #         rxdf.at[i, 'transmit.time'] = txdf.at[j, 'Timestamp']
    #         rxdf.at[i, 'transmit.time_epoch'] = txdf.at[j, 'Timestamp_epoch']
    # df = rxdf
    
    rxseq = rxdf['sequence.number'].array
    txseq = txdf['sequence.number'].array
    txts = txdf['Timestamp'].array
    txts_epoch= txdf['Timestamp_epoch'].array
    rx_txts_arr = []
    rx_txts_epoch_arr = []
    # print(len(txdf))
    # print(len(rxdf))
    j = 0
    N = len(txdf)
    M = len(rxdf)
    for i in tqdm(range(len(rxseq))):
        while j != N and txseq[j] != rxseq[i]:
            j += 1
        if j != N:
            rx_txts_arr.append(txts[j])
            rx_txts_epoch_arr.append(txts_epoch[j])
    df = rxdf.join(pd.DataFrame({'transmit.time' : rx_txts_arr, 'transmit.time_epoch' : rx_txts_epoch_arr}))
    
    df.dropna(how='any', subset=['transmit.time', 'transmit.time_epoch'], axis=0, inplace=True)
    df.rename(
        columns={
            "Timestamp": "arrival.time",
            "Timestamp_epoch": "arrival.time_epoch",
            "payload.time": "Timestamp",
            "payload.time_epoch": "Timestamp_epoch",
        }, inplace=True
    )
    df["lost"] = False
    df["latency"] = 0
    df = df[["sequence.number", "Timestamp", "Timestamp_epoch", "lost", "latency", "transmit.time", "transmit.time_epoch", "arrival.time", "arrival.time_epoch"]]
    
    return df

def interp(x, y, ratio):
    """
    Interpolation

    Args:
        x, y (datetime.datetime)
        ratio (float): a decimal numeral in a range [0, 1]
    Returns:
        (datetime.datetime): breakpoint of interpolation
    """
    return x + (y - x) * ratio

def get_compensate(df, mode, delta1=None, delta2=None):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # payload.time
    df['transmit.time'] = pd.to_datetime(df['transmit.time'])
    df['arrival.time'] = pd.to_datetime(df['arrival.time'])
    if mode == "dl":
        benchmark = list(df["transmit.time"].array)
    elif mode == "ul":
        benchmark = list(df["arrival.time"].array)
    bm1, bm2 = benchmark[0], benchmark[-1]
    ratio1 = (bm1-delta1[0]).total_seconds() / (delta2[0]-delta1[0]).total_seconds()
    ratio2 = (bm2-delta1[0]).total_seconds() / (delta2[0]-delta1[0]).total_seconds()
    _delta1 = interp(delta1[1], delta2[1], ratio1)
    _delta2 = interp(delta1[1], delta2[1], ratio2)
    # print(_delta1, _delta2)
    epoch_comp_list = list(np.round(np.linspace(_delta1, _delta2, len(df)), 6))
    comp_list = pd.to_timedelta(epoch_comp_list, "sec")
    # print(comp_list)
    # display(df)
    if mode == "dl":
        df['arrival.time_epoch'] = df['arrival.time_epoch'].add(pd.Series(epoch_comp_list))
        df['arrival.time'] = df['arrival.time'].add(pd.Series(comp_list))
    elif mode == "ul":
        df['Timestamp_epoch'] = df['Timestamp_epoch'].add(pd.Series(epoch_comp_list))
        df['Timestamp'] = df['Timestamp'].add(pd.Series(comp_list))
        df['transmit.time_epoch'] = df['transmit.time_epoch'].add(pd.Series(epoch_comp_list))
        df['transmit.time'] = df['transmit.time'].add(pd.Series(comp_list))
    # display(df)
    return df

def get_latency_jitter(df, mode):
    # define latnecy := arrival.time - payload.time
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # payload.time
    df['transmit.time'] = pd.to_datetime(df['transmit.time'])
    df['arrival.time'] = pd.to_datetime(df['arrival.time'])

    ### calculate latency
    # print(df['latency'])
    # print(df['latency'][df['lost'] == False])
    # df.loc[:, df['lost'] == True]['latency'] = np.inf
    # df.loc[:, df['lost'] == False]['latency'] = (df.loc[:, df['lost'] == False]['arrival.time'] - df.loc[:, df['lost'] == False]['Timestamp']).dt.total_seconds().round(6)
    df['latency'] = float('inf')
    df.loc[df['lost'] == False, 'latency'] = (df.loc[df['lost'] == False, 'arrival.time'] - df.loc[df['lost'] == False, 'Timestamp']).dt.total_seconds().round(6)
    # df['latency'] = (df['arrival.time'] - df['Timestamp']).dt.total_seconds().round(6)
    # display(df)
    
    ### no other way!!!
    # bm = (5 + random.randint(-2000, 2000)*1e-3) * 1e-3
    # # latndf = df['latency'][df['lost'] == False]
    # latndf = df.loc[df['lost'] == False, 'latency']
    # minlatn = min(latndf)
    # epoch_comp = bm - minlatn
    # comp = pd.to_timedelta(epoch_comp, "sec")
    # # print(epoch_comp)
    # # print(comp)
    # if mode == "dl":
    #     df['arrival.time_epoch'] = df['arrival.time_epoch'] + epoch_comp
    #     df['arrival.time'] = df['arrival.time'] + comp
    # elif mode == "ul":
    #     df['Timestamp_epoch'] = df['Timestamp_epoch'] - epoch_comp
    #     df['Timestamp'] = df['Timestamp'] - comp
    #     df['transmit.time_epoch'] = df['transmit.time_epoch'] - epoch_comp
    #     df['transmit.time'] = df['transmit.time'] - comp
    # # df['latency'] = (df['arrival.time'] - df['Timestamp']).dt.total_seconds().round(6)
    # # df.loc[:, df['lost'] == False]['latency'] = (df.loc[:, df['lost'] == False]['arrival.time'] - df.loc[:, df['lost'] == False]['Timestamp']).dt.total_seconds().round(6)
    # df.loc[df['lost'] == False, 'latency'] = (df.loc[df['lost'] == False, 'arrival.time'] - df.loc[df['lost'] == False, 'Timestamp']).dt.total_seconds().round(6)
    
    return df

def get_statistics(df, fout1, fout2, fout3):
    # output packet record csv
    df['excl'] = df['latency'] > 100e-3
    # df.loc[df['lost'] == False, 'excl'] = df.loc[df['lost'] == False, 'latency'] > 100e-3
    df = df[["sequence.number", "Timestamp", "Timestamp_epoch", "lost", "excl", "latency", "transmit.time", "transmit.time_epoch", "arrival.time", "arrival.time_epoch"]]
    print("output >>>", fout1)
    df.to_csv(fout1, index=False)
    
    # loss statistics
    total_packet_sent = len(df)
    total_loss = len(df[df["lost"] == True])
    loss_rate = total_loss / (total_packet_sent + 1e-9) * 100  # ratio (%)
    exp_time = round(df['Timestamp_epoch'].iloc[-1] - df['Timestamp_epoch'].iloc[0], 6) if total_packet_sent else 0
    print("output >>>", fout2)
    with open(fout2, "w", newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(['total_packet_sent', 'total_packet_loss', 'packet_loss_rate(%)', 'experiment_time(sec)'])
        writer.writerow([total_packet_sent, total_loss, loss_rate, exp_time])
    
    # latency statistics
    latndf = df['latency'][df['lost'] == False]
    total_packet_recv = len(latndf)
    total_excs_latency = len(latndf[latndf > 100e-3])
    excs_latency_rate = total_excs_latency / (total_packet_recv + 1e-9) * 100  # ratio (%)
    
    print("output >>>", fout3)
    with open(fout3, "w", newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(['total_packet_recv', 'total_excessive_latency', 'excessive_latency_rate(%)', 'experiment_time(sec)'])
        writer.writerow([total_packet_recv, total_excs_latency, excs_latency_rate, exp_time])
        
    # print(min(latndf), max(latndf), mean(latndf), stdev(latndf))
    
    print("------------------------------------------")
    print("min latency:         ", min(latndf), "seconds")
    print("max latency:         ", max(latndf), "seconds")
    print("mean latency:        ", round(mean(latndf), 6), "seconds")
    print("stdev latency:       ", round(stdev(latndf), 6), "seconds")
    print("total_packet_sent:   ", total_packet_sent)
    print("total_packet_recv:   ", total_packet_recv)
    print("total_packet_loss:   ", total_loss)
    print("packet_loss_rate(%): ", round(loss_rate, 3), "%")
    print("total_excs_latency:  ", total_excs_latency)
    print("excs_latency_rate(%):", round(excs_latency_rate, 3), "%")
    print("experiment_time(sec):", exp_time, "seconds")
    print("------------------------------------------")
    print()


# dl_txdf = pd.read_csv("/home/wmnlab/D/database/2023-02-04#2/_Bandlock_Udp_all_RM500Q/qc01/#01/middle/udp_dnlk_server_pkt_brief.csv")
# dl_rxdf = pd.read_csv("/home/wmnlab/D/database/2023-02-04#2/_Bandlock_Udp_all_RM500Q/qc01/#01/middle/udp_dnlk_client_pkt_brief.csv")
# ul_txdf = pd.read_csv("/home/wmnlab/D/database/2023-02-04#2/_Bandlock_Udp_all_RM500Q/qc01/#01/middle/udp_uplk_client_pkt_brief.csv")
# ul_rxdf = pd.read_csv("/home/wmnlab/D/database/2023-02-04#2/_Bandlock_Udp_all_RM500Q/qc01/#01/middle/udp_uplk_server_pkt_brief.csv")

# dl_txseq = list(dl_txdf["sequence.number"].array)
# dl_rxseq = list(dl_rxdf["sequence.number"].array)
# dlst = max(dl_txseq[0], dl_rxseq[0])
# dlet = min(dl_txseq[-1], dl_rxseq[-1])
# # print(dlst, dlet)

# ul_txseq = list(ul_txdf["sequence.number"].array)
# ul_rxseq = list(ul_rxdf["sequence.number"].array)
# ulst = max(ul_txseq[0], ul_rxseq[0])
# ulet = min(ul_txseq[-1], ul_rxseq[-1])
# # print(ulst, ulet)

# st = max(dlst, ulst)
# et = min(dlet, ulet)
# # print("----------------")
# st += PKT_RATE * 5  # 開頭切5秒
# et -= PKT_RATE * 5  # 結尾切5秒
# # print(st, et)

# dl_txdf = dl_txdf[(dl_txdf["sequence.number"] >= st) & (dl_txdf["sequence.number"] <= et)]
# dl_rxdf = dl_rxdf[(dl_rxdf["sequence.number"] >= st) & (dl_rxdf["sequence.number"] <= et)]
# ul_txdf = ul_txdf[(ul_txdf["sequence.number"] >= st) & (ul_txdf["sequence.number"] <= et)]
# ul_rxdf = ul_rxdf[(ul_rxdf["sequence.number"] >= st) & (ul_rxdf["sequence.number"] <= et)]

# dl_txdf.reset_index(drop=True, inplace=True)
# dl_rxdf.reset_index(drop=True, inplace=True)
# ul_txdf.reset_index(drop=True, inplace=True)
# ul_rxdf.reset_index(drop=True, inplace=True)

# with open("/home/wmnlab/D/database/2023-02-04#2/tsync/qc01/delta.txt", encoding="utf-8") as f:
#     lines = f.readlines()
#     timerec1 = pd.to_datetime(lines[0])
#     epoch_delta1 = float(lines[1])
#     timedelta1 = pd.Timedelta(seconds=epoch_delta1).round('us')
# with open("/home/wmnlab/D/database/2023-02-04#2/tsync/qc01/delta1.txt", encoding="utf-8") as f:
#     lines = f.readlines()
#     timerec2 = pd.to_datetime(lines[0])
#     epoch_delta2 = float(lines[1])
#     timedelta2 = pd.Timedelta(seconds=epoch_delta2).round('us')

# # print(timerec1)
# # print(epoch_delta1)
# # print(timedelta1)
# # print(timerec2)
# # print(epoch_delta2)
# # print(timedelta2)
# delta1 = (timerec1, epoch_delta1, timedelta1)
# delta2 = (timerec2, epoch_delta2, timedelta2)



if __name__ == "__main__":
    t = TicToc()  # create instance of class
    t.tic()  # Start timer
    # --------------------- (3) decode a batch of files (User Settings) ---------------------
    # err_handles = []
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
            
    # --------------------- Phase 2: Parse packet loss & latency --------------------- 
    ### Read files
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
                    target_dir1 = os.path.join(database, date, expr, dev, trace, "data")
                    target_dir2 = os.path.join(database, date, expr, dev, trace, "statistics")
                    if expr == "tsync":
                        source_dir = os.path.join(database, date, expr, dev, trace)
                        target_dir = os.path.join(database, date, expr, dev, trace)
                    makedir(target_dir1)
                    makedir(target_dir2)
                    filenames = os.listdir(source_dir)
                    t1 = TicToc()  # create instance of class
                    t1.tic()  # Start timer
                    dl_txdf = pd.read_csv(os.path.join(source_dir, "udp_dnlk_server_pkt_brief.csv"))
                    dl_rxdf = pd.read_csv(os.path.join(source_dir, "udp_dnlk_client_pkt_brief.csv"))
                    ul_txdf = pd.read_csv(os.path.join(source_dir, "udp_uplk_client_pkt_brief.csv"))
                    ul_rxdf = pd.read_csv(os.path.join(source_dir, "udp_uplk_server_pkt_brief.csv"))
                    
                    dl_txseq = list(dl_txdf["sequence.number"].array)
                    dl_rxseq = list(dl_rxdf["sequence.number"].array)
                    dlst = max(dl_txseq[0], dl_rxseq[0])
                    dlet = min(dl_txseq[-1], dl_rxseq[-1])
                    # print(dlst, dlet)

                    ul_txseq = list(ul_txdf["sequence.number"].array)
                    ul_rxseq = list(ul_rxdf["sequence.number"].array)
                    ulst = max(ul_txseq[0], ul_rxseq[0])
                    ulet = min(ul_txseq[-1], ul_rxseq[-1])
                    # print(ulst, ulet)

                    st = max(dlst, ulst)
                    et = min(dlet, ulet)
                    # print("----------------")
                    st += PKT_RATE * 5  # 開頭切5秒
                    et -= PKT_RATE * 5  # 結尾切5秒
                    # print(st, et)

                    dl_txdf = dl_txdf[(dl_txdf["sequence.number"] >= st) & (dl_txdf["sequence.number"] <= et)]
                    dl_rxdf = dl_rxdf[(dl_rxdf["sequence.number"] >= st) & (dl_rxdf["sequence.number"] <= et)]
                    ul_txdf = ul_txdf[(ul_txdf["sequence.number"] >= st) & (ul_txdf["sequence.number"] <= et)]
                    ul_rxdf = ul_rxdf[(ul_rxdf["sequence.number"] >= st) & (ul_rxdf["sequence.number"] <= et)]

                    dl_txdf.reset_index(drop=True, inplace=True)
                    dl_rxdf.reset_index(drop=True, inplace=True)
                    ul_txdf.reset_index(drop=True, inplace=True)
                    ul_rxdf.reset_index(drop=True, inplace=True)
                    
                    ### Timedelta
                    # timedelta, epoch_delta = calc_delta(txdl_df, rxdl_df, txul_df, rxul_df)
                    # with open(os.path.join(database, date, "tsync", dev, "delta.txt"), encoding="utf-8") as f:
                    #     lines = f.readlines()
                    #     timerec1 = pd.to_datetime(lines[0])
                    #     epoch_delta1 = float(lines[1])
                    #     timedelta1 = pd.Timedelta(seconds=epoch_delta1).round('us')
                    # with open(os.path.join(database, date, "tsync", dev, "delta1.txt"), encoding="utf-8") as f:
                    #     lines = f.readlines()
                    #     timerec2 = pd.to_datetime(lines[0])
                    #     epoch_delta2 = float(lines[1])
                    #     timedelta2 = pd.Timedelta(seconds=epoch_delta2).round('us')
                    # delta1 = (timerec1, epoch_delta1, timedelta1)
                    # delta2 = (timerec2, epoch_delta2, timedelta2)
                    
                    # print(timerec1)
                    # print(epoch_delta1)
                    # print(timedelta1)
                    # print(timerec2)
                    # print(epoch_delta2)
                    # print(timedelta2)

                    ### Downlink
                    fout1_dl = os.path.join(target_dir1, "udp_dnlk_loss_latency.csv")
                    fout2_dl = os.path.join(target_dir2, "udp_dnlk_loss_statistics.csv")
                    fout3_dl = os.path.join(target_dir2, "udp_dnlk_excl_statistics.csv")
                    
                    lossdf = get_loss(dl_txdf.copy(), dl_rxdf.copy())
                    latndf = get_match(dl_txdf.copy(), dl_rxdf.copy())
                    df = pd.concat([lossdf, latndf], axis=0)
                    df.sort_values(by=["sequence.number"], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    # df = get_compensate(df.copy(), "dl", delta1, delta2)
                    df = get_latency_jitter(df.copy(), "dl")
                    get_statistics(df.copy(), fout1_dl, fout2_dl, fout3_dl)
                    
                    ### Uplink
                    fout1_ul = os.path.join(target_dir1, "udp_uplk_loss_latency.csv")
                    fout2_ul = os.path.join(target_dir2, "udp_uplk_loss_statistics.csv")
                    fout3_ul = os.path.join(target_dir2, "udp_uplk_excl_statistics.csv")
                    
                    lossdf = get_loss(ul_txdf.copy(), ul_rxdf.copy())
                    latndf = get_match(ul_txdf.copy(), ul_rxdf.copy())
                    df = pd.concat([lossdf, latndf], axis=0)
                    df.sort_values(by=["sequence.number"], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    # df = get_compensate(df.copy(), "ul", delta1, delta2)
                    df = get_latency_jitter(df.copy(), "ul")
                    get_statistics(df.copy(), fout1_ul, fout2_ul, fout3_ul)
                    
                    t1.toc()
    # ### Check errors
    # flag = False
    # for err_handle in err_handles:
    #     flag = error_handling(err_handle)
    # if not flag:
    #     print("**************************************************")
    #     print("No error occurs!!")
    #     print("**************************************************")
    t.toc()  # Time elapsed since t.tic()
