#!/usr/bin/python
# Filename: online-analysis-example.py
import os
import datetime as dt
import argparse
import json
import threading
# import multiprocessing
import time

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
# from mobile_insight.analyzer import MyAnalyzer

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
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    savepath = os.path.join("/home/wmnlab/Data/mobileinsight", f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(savepath)

    # Enable all
    # src.enable_log_all()

    # Enable 3G/4G/5G RRC (radio resource control) monitoring
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    # src.enable_log("WCDMA_RRC_OTA_Packet")
    # src.enable_log("5G_NR_PDCP_UL_Control_Pdu")
    # src.enable_log("5G_NR_L2_UL_TB")
    # src.enable_log("5G_NR_L2_UL_BSR")
    # src.enable_log("5G_NR_RLC_DL_Stats")
    # src.enable_log("5G_NR_MAC_UL_TB_Stats")
    # src.enable_log("5G_NR_MAC_UL_Physical_Channel_Schedule_Report")
    # src.enable_log("5G_NR_MAC_PDSCH_Stats")
    # src.enable_log("5G_NR_MAC_RACH_Trigger")
    src.enable_log("5G_NR_ML1_Searcher_Measurement_Database_Update_Ext")
    src.enable_log('LTE_PHY_Connected_Mode_Intra_Freq_Meas')

    # Myanalyzer
    # myanalyzer = MyAnalyzer()
    # myanalyzer.set_source(src)

    # 5G NR RRC analyzer
    # nr_rrc_analyzer = NrRrcAnalyzer()
    # nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # 4G RRC analyzer
    # lte_rrc_analyzer = LteRrcAnalyzer()
    # lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # 3G RRC analyzer
    # wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    # wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # 4G Nas analyzer
    # lte_nas_analyzer = LteNasAnalyzer()
    # lte_nas_analyzer.set_source(src)

    # 4G Phy analyzer
    # lte_phy_analyzer = LtePhyAnalyzer()
    # lte_phy_analyzer.set_source(src)

    # 4G Rlc analyzer
    # lte_rlc_analyzer = LteRlcAnalyzer()
    # lte_rlc_analyzer.set_source(src)

    # 4G Mac analyzer
    # lte_mac_analyzer = LteMacAnalyzer()
    # lte_mac_analyzer.set_source(src)

    # 4G Pdcp analyzer
    # lte_pdcp_analyzer = LtePdcpAnalyzer()
    # lte_pdcp_analyzer.set_source(src)

    # Dump the messages to std I/O. Comment it if it is not needed.
    dumper = MsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MsgLogger.XML)  # decode the message as xml
    
    # self defined analyzer
    # save_path = '/home/wmnlab/test.csv'
    # myanalyzer = MyAnalyzer(save_path)
    # myanalyzer.set_source(src)

    # Start the monitoring
    src.run()

    # def run():
    #     src.run()

    # t = threading.Thread(target=run, daemon=True)
    # t.start()

    # time.sleep(1)
    # myanalyzer.reset()
    
    # while True:
    #     # print(myanalyzer.RRC_DICT)
    #     myanalyzer.to_featuredict()
    #     S = myanalyzer.get_featuredict()
    #     print('=====================================')
    #     for k in S:
    #         print(k, ':', S[k])
    #     myanalyzer.reset()
    #     time.sleep(1)