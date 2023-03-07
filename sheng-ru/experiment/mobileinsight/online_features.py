#!/usr/bin/python
# Filename: online-features.py
import os
import sys
import time
import threading
import datetime as dt
import argparse
import json
import torch
from model.model import RNN_Classifier

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer


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
        os.makedirs("/home/wmnlab/Data/mobileinsight")

    # Initialize online monitors
    src1 = OnlineMonitor()
    src1.set_serial_port(ser1)  # the serial port to collect the traces
    src1.set_baudrate(baudrate)  # the baudrate of the port
    src1.save_log_as(savepath)

    src2 = OnlineMonitor()
    src2.set_serial_port(ser2)  # the serial port to collect the traces
    src2.set_baudrate(baudrate)  # the baudrate of the port
    src2.save_log_as(savepath)

    # Set analyzer
    myanalyzer1 = MyAnalyzer()
    myanalyzer1.set_source(src1)

    myanalyzer2 = MyAnalyzer()
    myanalyzer2.set_source(src2)

    # Online features collected.
    def run1():
        src1.run()

    def run2():
        src2.run()

    t1 = threading.Thread(target=run1)
    t1.setDaemon(True)
    t1.start()    
    
    t2 = threading.Thread(target=run2)
    t2.setDaemon(True)
    t2.start()

    def get_tensor_input():
        
        L = []

        for featuredict in [myanalyzer1.get_featuredict(), myanalyzer2.get_featuredict()]:
            for key in featuredict:
                L.append(featuredict[key])

        return torch.FloatTensor(L)
    
    time.sleep(1) # Fill up feature_dict buffer first
    time_seq = 15
    print(f"Fill up time series data first. Please wait for about {time_seq} second.")

    count = 0
    input = torch.FloatTensor([])

    classifier = torch.load('model/best_model_loss.pt')
    classifier.eval()

    while True:
        myanalyzer1.to_featuredict()
        myanalyzer2.to_featuredict()
        
        x = get_tensor_input()

        if count < time_seq-1:
            input = torch.cat((input, torch.unsqueeze(x, dim=0)), dim=0)
            count+=1
        else:
            input = torch.cat((input, torch.unsqueeze(x, dim=0)), dim=0)
            out = classifier(input.unsqueeze(dim=0)).item()
            print(out)
            input = input[:-1]
            
        myanalyzer1.reset()
        myanalyzer2.reset()
        time.sleep(1)
        