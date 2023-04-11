#!/usr/bin/python
# Filename: online-features.py

import os
import sys
import subprocess
import time
import threading
import datetime as dt
import argparse
import json
import re
import pandas as pd
import torch
from model.model import RNN_Forecaster

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer

# For create deep learning input 
def get_tensor_input():
    
    L = []

    for featuredict in [myanalyzer1.get_featuredict(), myanalyzer2.get_featuredict()]:
        for key in featuredict:
            L.append(featuredict[key])

    return torch.FloatTensor(L)

# Query modem current band setting
def query_band(dev):

    out = subprocess.check_output(f'./band-setting.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    inds = [m.start() for m in re.finditer("lte_band", out)]
    inds2 = [m.start() for m in re.finditer("\r", out)]
    result = out[inds[1]+len('"lte_band"'):inds2[2]]

    return 'B'+result

# get ecperiment time
def get_current_tp(x):

    for i, time_point in enumerate(tps):
        if x < time_point:
            y = i
            break
        try: y
        except:
            y = 9

    return y

# Change band function
def change_band(dev, band):
    original = query_band(dev)
    subprocess.Popen([f'./band-setting.sh -i {dev} -l {band}'], shell=True)
    new = query_band(dev)
    print(f"Change {dev} from {original} to {new}.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, nargs='+', help="device: e.g. qc00 qc01")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()

    if args.device is None or len(args.device) != 2:
        print("Please specified 2 device, e.g. -d qc00 qc01")
        sys.exit(1)

    baudrate = args.baudrate
    dev1, dev2 = args.device[0], args.device[1]
    
    f = open('device_to_serial.json')
    device_to_serial = json.load(f)
    ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
    f.close()

    ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
    ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    # makedir if not exist
    if not os.path.exists("/home/wmnlab/Data/mobileinsight"):
        # if the demo_folder directory is not present 
        # then create it.
        print('Build directory: /home/wmnlab/Data/mobileinsight')
        os.makedirs("/home/wmnlab/Data/mobileinsight")

    # Initialize online monitors
    src1 = OnlineMonitor()
    src1.set_serial_port(ser1)  # the serial port to collect the traces
    src1.set_baudrate(baudrate)  # the baudrate of the port

    src2 = OnlineMonitor()
    src2.set_serial_port(ser2)  # the serial port to collect the traces
    src2.set_baudrate(baudrate)  # the baudrate of the port

    # Set analyzer
    myanalyzer1 = MyAnalyzer()
    myanalyzer1.set_source(src1)
    
    myanalyzer2 = MyAnalyzer()
    myanalyzer2.set_source(src2)
    
    # Online features collected.
    def run1():
        # save_path1 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev1}_{t}.txt")
        # src1.save_log_as(save_path1)
        src1.run()

    def run2():
        # save_path2 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev2}_{t}.txt")
        # src2.save_log_as(save_path2)
        src2.run()

    t1 = threading.Thread(target=run1, daemon=True)
    t1.start()    
    
    t2 = threading.Thread(target=run2, daemon=True)
    t2.start()

    # For ML model running
    count = 0
    x_in = torch.FloatTensor([])

    forecaster = torch.load('model/preformance_predict.pt', map_location=torch.device('cpu'))
    forecaster.eval()

    # Record log
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f'{t}.csv')
    f_out = open(save_path, 'w')
    f_out.write(','.join(['LTE_HO, MN_HO', 'SN_setup', 'SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                          'num_of-neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1', 'RSRP2', 'RSRQ2',
                          'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1', 'nr-RSRP2', 'nr-RSRQ2']*2)+',out\n')

    # For cleaning features before experiment
    time_seq = 30
    print(f"Fill up time series data first. Please wait for about {time_seq} second.")
    time.sleep(1) # Clean time
    myanalyzer1.reset()
    myanalyzer2.reset()
    time.sleep(1) # buffer time

    # Open database
    database = pd.read_csv('database.csv')
    tps = list(range(30, 330, 30)) # Time points

    # For manual control start time 
    start = False

    def start_inference():
        global start, count

        read = input('Start inference(y/n)? ')

        if read == 'y':
            start = True
        else:
            start = False


        if count < time_seq:
            print(f'{time_seq-count} more second...')
        else:
            print('Start immediately!')

    t_s = threading.Thread(target=start_inference, daemon=True)
    t_s.start()

    # cd modem-utilities to run code
    os.chdir("../../../modem-utilities/")
    
    # Main Process
    try:

        while True: 

            myanalyzer1.to_featuredict()
            myanalyzer2.to_featuredict()
            
            x = get_tensor_input()

            if count < time_seq-1 or not start:
                
                x_in = torch.cat((x_in, torch.unsqueeze(x, dim=0)), dim=0)
                y = [str(a) for a in torch.Tensor.tolist(x)]
                f_out.write(','.join(y) + '\n')
            
            else:
                
                x_in = torch.cat((x_in, torch.unsqueeze(x, dim=0)), dim=0)
                out = forecaster(x_in.unsqueeze(dim=0)).detach().numpy()
                y = [str(a) for a in torch.Tensor.tolist(x)]
                f_out.write(','.join(y) + f',{out}'+',\n')
                print(out)

                # if out > 0.5:
                # AB = sorted([query_band(dev1), query_band(dev2)])
                # A, B = AB[0], AB[1]
                # current_settings = A+'&'+B
                # tp_now = get_current_tp(count)
                # print(current_settings)

                # print(database[current_settings].iloc[tp_now])
                
                x_in = x_in[:-1]
                
            count += 1
            myanalyzer1.reset()
            myanalyzer2.reset()
            time.sleep(1)

    except KeyboardInterrupt:
        
        f_out.close()