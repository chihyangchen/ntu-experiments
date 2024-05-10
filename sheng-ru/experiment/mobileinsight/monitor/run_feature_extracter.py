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
    feature_extracter = FeatureExtracter(mode='intensive')
    feature_extracter.set_source(src)

    # Use threading to start the monitoring
    def run_src(): src.run()
    t_src = threading.Thread(target=run_src, daemon=True)
    t_src.start()  
    
    time_slot = 0.1
    
    time.sleep(.5) # Clean time
    feature_extracter.reset()
    feature_extracter.reset_intensive_L()
    time.sleep(1) # buffer time 
    
    try:
        while True:
            start_time = dt.datetime.now()
            feature_extracter.gather_intensive_L()
            feature_extracter.to_featuredict()
            features = feature_extracter.get_featuredict()
            print(features)
            feature_extracter.remove_intensive_L_by_time(start_time - dt.timedelta(seconds=1-time_slot))
            feature_extracter.reset()
            time.sleep(time_slot)
    except Exception as e: 
        print(e)
        exit(0)