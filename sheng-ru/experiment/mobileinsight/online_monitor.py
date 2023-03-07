#!/usr/bin/python
# Filename: online-analysis-example.py
import os
import sys
import argparse
import json
import threading
# import multiprocessing
import time

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, help="device: e.g. qc00")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()

    baudrate = args.baudrate
    dev = args.device
    f = open('device_to_serial.json')
    device_to_serial = json.load(f)
    ser = device_to_serial[dev]
    f.close()

    ser = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser}-if00-port0")

    # Initialize a 3G/4G/5G monitor
    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port

    # Enable 3G/4G/5G RRC (radio resource control) monitoring
    # src.enable_log("5G_NR_RRC_OTA_Packet")
    # src.enable_log("LTE_RRC_OTA_Packet")
    # src.enable_log("WCDMA_RRC_OTA_Packet")

    # Myanalyzer
    myanalyzer = MyAnalyzer()
    myanalyzer.set_source(src)

    # 5G NR RRC analyzer
    # nr_rrc_analyzer = NrRrcAnalyzer()
    # nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # 4G RRC analyzer
    # lte_rrc_analyzer = LteRrcAnalyzer()
    # lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # 3G RRC analyzer
    # wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    # wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    # src.run()

    def run():
        src.run()

    t = threading.Thread(target=run, daemon=True)
    t.start()

    while True:
        myanalyzer.to_featuredict()
        print(myanalyzer.get_featuredict())
        myanalyzer.reset()
        time.sleep(1)