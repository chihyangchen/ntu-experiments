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
import numpy as np

# Machine Learning Model
import xgboost as xgb

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer

class Predicter():

    def __init__(self, lte_cls, nr_cls, lte_fst, nr_fst, set_up, rlf):
        
        self.lte_clssifier  = xgb.Booster()
        self.lte_clssifier.load_model(lte_cls)

        self.nr_clssifier  = xgb.Booster()
        self.nr_clssifier.load_model(nr_cls)
        
        self.lte_forecaster = xgb.Booster()
        self.lte_forecaster.load_model(lte_fst)

        self.nr_forecaster =  xgb.Booster()
        self.nr_forecaster.load_model(nr_fst)

        self.setup_clssifier =  xgb.Booster()
        self.setup_clssifier.load_model(set_up)

        self.rlf_clssifier =  xgb.Booster()
        self.rlf_clssifier.load_model(rlf)

    def foward(self, x_in):

        o1 = self.lte_clssifier.predict(x_in)
        o2 = self.nr_clssifier.predict(x_in)
        o3 = self.lte_forecaster.predict(x_in)
        o4 = self.nr_forecaster.predict(x_in)
        o5 = self.setup_clssifier.predict(x_in)
        o6 = self.rlf_clssifier.predict(x_in)

        out = [o1,o2,o3,o4,o5,o6]
        out = [o.item() for o in out]

        return out

selected_features = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                     'num_of_neis','RSRP', 'RSRQ', 'RSRP1','RSRQ1',
                     'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1','nr-RSRQ1']

def get_array_features(analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in selected_features}

    return np.array(list(features.values()))

# Query modem current band setting
def query_band(dev):

    out = subprocess.check_output(f'./band-setting.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    inds = [m.start() for m in re.finditer("lte_band", out)]
    inds2 = [m.start() for m in re.finditer("\r", out)]
    result = out[inds[1]+len('"lte_band"'):inds2[2]]

    return 'B'+result

# Change band function
def change_band(dev, band):
    original = query_band(dev)
    subprocess.Popen([f'./band-setting.sh -i {dev} -l {band}'], shell=True)
    new = query_band(dev)
    print(f"Change {dev} from {original} to {new}.")


# show
HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']

def show_HO(analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'HO {k} happened!!!!!')

def show_predictions(predictions):

    thr = 0.5
    if predictions[0] > thr:
        print(f'Prediciotn: {predictions[2]} remaining LTE Ho happen!!!')
    if predictions[1] > thr:
        print(f'Prediciotn: {predictions[3]} remaining LTE Ho happen!!!')
    if predictions[4] > thr:
        print(f'Prediciotn: Near NR setup!!!')
    if predictions[5] > thr:
        print(f'Prediciotn: Near RLF!!!')


# get experiment time
def get_current_tp(x):

    for i, time_point in enumerate(tps):
        if x < time_point:
            y = i
            break
        try: y
        except:
            y = 9

    return y

# Design Action here!!
def Action():

    pass

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
    
    with open('device_to_serial.json', 'r') as f:
        device_to_serial = json.load(f)
        ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
        ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
        ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    # makedir if not exist
    if not os.path.exists("/home/wmnlab/Data/mobileinsight"):
        # if the demo_folder directory is not present 
        # then create it.
        print('Build directory: /home/wmnlab/Data/mobileinsight')
        os.makedirs("/home/wmnlab/Data/mobileinsight")

    # Loading Model
    lte_classifier = 'model/lte_HO_cls_xgb.json'
    nr_classifier = 'model/nr_HO_cls_xgb.json'
    lte_forecaster = 'model/lte_HO_fcst_xgb.json'
    nr_forecaster = 'model/nr_HO_fcst_xgb.json'
    setup_classifier = 'model/setup_cls_xgb.json'
    rlf_classifier = 'model/rlf_cls_xgb.json'
    predictor1 = Predicter(lte_classifier, nr_classifier, lte_forecaster, nr_forecaster, setup_classifier, rlf_classifier)
    predictor2 = Predicter(lte_classifier, nr_classifier, lte_forecaster, nr_forecaster, setup_classifier, rlf_classifier)

    # Record
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f'record2_{t}.csv')
    f_out = open(save_path, 'w')
    f_out.write(','.join(['LTE_HO, MN_HO', 'SN_setup', 'SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                          'num_of-neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1',
                          'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1',
                          'lte_cls','nr_cls','lte_fst','nr_fst','setup_cls','rlf_cls']*2) + '\n')
    
    # Initialize online monitors
    src1 = OnlineMonitor()
    src1.set_serial_port(ser1)  # the serial port to collect the traces
    src1.set_baudrate(baudrate)  # the baudrate of the port

    src2 = OnlineMonitor()
    src2.set_serial_port(ser2)  # the serial port to collect the traces
    src2.set_baudrate(baudrate)  # the baudrate of the port

    # Set analyzer
    save_path1 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev1}_{t}.txt")
    myanalyzer1 = MyAnalyzer(save_path1)
    myanalyzer1.set_source(src1)
    
    save_path2 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev2}_{t}.txt")
    myanalyzer2 = MyAnalyzer(save_path2)
    myanalyzer2.set_source(src2)
    
    # Online features collected.
    def run_src(src):
        src.run()
    
    # save_path1 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev1}_{t}.mi2log")
    # src1.save_log_as(save_path1)
    # save_path2 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev2}_{t}.mi2log")
    # src2.save_log_as(save_path2)

    t1 = threading.Thread(target=run_src, args=[src1], daemon=True)
    t1.start()    
    
    t2 = threading.Thread(target=run_src, args=[src2], daemon=True)
    t2.start()

    # For ML model running
    time.sleep(.5) # Clean time
    myanalyzer1.reset(); myanalyzer2.reset()
    time.sleep(1) # buffer time

    time_seq = 20
    count = 1

    # cd modem-utilities to run code
    os.chdir("../../../modem-utilities/")
    
    # Main Process
    try:

        while True: 
            
            start = time.time()
            myanalyzer1.to_featuredict()
            myanalyzer2.to_featuredict()
            
            features1 = get_array_features(myanalyzer1)
            features2 = get_array_features(myanalyzer2)

            if count <= time_seq:
                
                if count == 1: 

                    x_in1 = features1
                    x_in2 = features2

                else:

                    x_in1 = np.concatenate((x_in1, features1), axis=0)
                    x_in2 = np.concatenate((x_in2, features2), axis=0)

                print(f'{20-count} second after start...')
                print(count, x_in1.shape, x_in2.shape)
                count += 1

                # record
                w1 = [str(e) for e in list(features1)]
                w2 = [str(e) for e in list(features2)]
                f_out.write(','.join(w1 + ['']*6 + w2) + ',\n') 

            else:
                
                x_in1 = np.concatenate((x_in1[len(selected_features):], features1), axis=0)
                x_in2 = np.concatenate((x_in2[len(selected_features):], features2), axis=0)
                

                x_in1_D = xgb.DMatrix(x_in1.reshape(1,-1))
                x_in2_D = xgb.DMatrix(x_in2.reshape(1,-1))

                out1 = predictor1.foward(x_in1_D)
                out2 = predictor2.foward(x_in2_D)

                ############ Action Here ##############

                # show_predictions(out1)
                # show_predictions(out2)
                # Action()

                #######################################

                # record
                w = [str(e) for e in list(features1)+out1+list(features2)+out2]
                f_out.write(','.join(w) + ',\n')
    
            myanalyzer1.reset()
            myanalyzer2.reset()

            end = time.time()
            time.sleep(1-(end-start))

    except KeyboardInterrupt:
        
        # Stop Record
        f_out.close()
        myanalyzer1.save_path = ''; myanalyzer1.f.close()
        myanalyzer2.save_path = ''; myanalyzer2.f.close()
        print("Ending code.")
    
        time.sleep(.2)
        sys.exit()