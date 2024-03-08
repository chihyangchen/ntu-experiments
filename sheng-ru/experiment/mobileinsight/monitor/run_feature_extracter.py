#!/usr/bin/python
# Filename: online-analysis-example.py
import os
import datetime as dt
import argparse
import json
import threading
import time

# Import MobileInsight modules
# from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import FeatureExtracter

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, help="device: e.g. qc00")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()

    baudrate = args.baudrate
    dev = args.device
    script_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(script_folder)
    d2s_path = os.path.join(parent_folder, 'device_to_serial.json')
    with open(d2s_path, 'r') as f:
        device_to_serial = json.load(f)
        ser = device_to_serial[dev]
        if dev.startswith('sm'):
            ser = os.path.join("/dev/serial/by-id", f"usb-SAMSUNG_SAMSUNG_Android_{ser}-if00-port0")
        elif dev.startswith('qc'):
            ser = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser}-if00-port0")

    # Initialize a 3G/4G/5G monitor
    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    savepath = os.path.join("/home/wmnlab/Data/mobileinsight", f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(savepath)

    # Dump the messages to std I/O. Comment it if it is not needed.
    # dumper = MsgLogger()
    # dumper.set_source(src)
    # dumper.set_decoding(MsgLogger.XML)  # decode the message as xml
    
    # self defined analyzer
    # Set analyzer
    featureextracter = FeatureExtracter()
    featureextracter.set_source(src)

    # Use threading to start the monitoring
    def run_src(): src.run()
    t_src = threading.Thread(target=run_src, daemon=True)
    t_src.start()  
    
    time.sleep(.5) # Clean time
    featureextracter.reset()
    time.sleep(1) # buffer time 
    
    try:

        while True:
            featureextracter.to_featuredict()
            features = featureextracter.get_featuredict()
            print(features)
            featureextracter.reset()
            time.sleep(1) 
            
    except: exit(0)