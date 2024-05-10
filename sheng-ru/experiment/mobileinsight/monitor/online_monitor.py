#!/usr/bin/python
# Filename: online-analysis-example.py
import os
import datetime as dt
import argparse
import json

# Import MobileInsight modules
from mobile_insight.analyzer import MsgLogger
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer, MyMsgLogger
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
    t = [str(x) for x in [now.year, now.month, now.day, now.hour, now.minute, now.second]]
    t = [x.zfill(2) for x in t]  # zero-padding to two digit
    t = '-'.join(t[:3]) + '_' + '-'.join(t[3:])
    savepath = os.path.join("/home/wmnlab/Data/mobileinsight", f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(savepath)

    # Enable all
    # src.enable_log_all()

    # Enable 3G/4G/5G RRC (radio resource control) monitoring
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("5G_NR_ML1_Searcher_Measurement_Database_Update_Ext")
    src.enable_log('LTE_PHY_Connected_Mode_Intra_Freq_Meas')

    # 5G NR RRC analyzer
    # nr_rrc_analyzer = NrRrcAnalyzer()
    # nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # 4G RRC analyzer
    # lte_rrc_analyzer = LteRrcAnalyzer()
    # lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # 3G RRC analyzer
    # wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    # wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Dump the messages to std I/O. Comment it if it is not needed.
    dumper = MyMsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MyMsgLogger.XML) 
    save_path = os.path.join('/home/wmnlab/Data/XML/', f"diag_log_{dev}_{t}.csv")
    dumper.save_decoded_msg_as(save_path)
        
    # self defined analyzer
    # save_path = '/home/wmnlab/test1.csv'
    # myanalyzer = MyAnalyzer(save_path)
    # myanalyzer.set_source(src)

    # Start the monitoring
    src.run()
