# Run Model with one device
# Author: Sheng-Ru Zeng

import os
import sys
import subprocess
import time
import threading
import argparse
import json
# import pandas as pd
import numpy as np
import datetime as dt

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

HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']

def get_array_features(analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in selected_features}

    return np.array(list(features.values()))

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

def Action():

    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, help="device: e.g. qc00 or sm00")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()

    baudrate = args.baudrate
    dev = args.device

    with open('device_to_serial.json', 'r') as f:
        device_to_serial = json.load(f)
        ser = device_to_serial[dev]
        ser = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser}-if00-port0")

    print(dev, baudrate, ser)

    # Loading Model
    lte_classifier = 'model/lte_HO_cls_xgb.json'
    nr_classifier = 'model/nr_HO_cls_xgb.json'
    lte_forecaster = 'model/lte_HO_fcst_xgb.json'
    nr_forecaster = 'model/nr_HO_fcst_xgb.json'
    setup_classifier = 'model/setup_cls_xgb.json'
    rlf_classifier = 'model/rlf_cls_xgb.json'
    predictor = Predicter(lte_classifier, nr_classifier, lte_forecaster, nr_forecaster, setup_classifier, rlf_classifier)

    # Record
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f'record_{t}.csv')
    f_out = open(save_path, 'w')
    f_out.write(','.join(['LTE_HO, MN_HO', 'SN_setup', 'SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                          'num_of-neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1',
                          'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1',
                          'lte_cls','nr_cls','lte_fst','nr_fst','setup_cls','rlf_cls']) + '\n')

    # Initialize online monitors
    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port

    # Set analyzer
    myanalyzer = MyAnalyzer()
    myanalyzer.set_source(src)

    save_path1 = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(save_path1)

    def run_src():
        src.run()

    t_src = threading.Thread(target=run_src, daemon=True)
    t_src.start()    

    time.sleep(.5) # Clean time
    myanalyzer.reset()
    time.sleep(1) # buffer time

    time_seq = 20
    count = 1

    try:

        while True:
            
            start = time.time()
            myanalyzer.to_featuredict()
            
            features = get_array_features(myanalyzer)

            if count <= time_seq:
                
                if count == 1: x_in = features
                else: x_in = np.concatenate((x_in, features), axis=0)

                print(f'{20-count} second after start...')
                # print(count, x_in.shape)
                count += 1

                # record
                w = [str(e) for e in list(features)]
                f_out.write(','.join(w) + ',\n') 

            else:
                
                x_in = np.concatenate((x_in[len(selected_features):], features), axis=0)
                
                x_in_D = xgb.DMatrix(x_in.reshape(1,-1))
                out = predictor.foward(x_in_D)

                ############ Action Here ##############

                show_predictions(out)

                # Action()

                #######################################

                # record
                w = [str(e) for e in list(features)+out]
                f_out.write(','.join(w) + ',\n')

            show_HO(myanalyzer)

            myanalyzer.reset()

            end = time.time()
            time.sleep(1-(end-start))

    except KeyboardInterrupt:
        
        f_out.close()
        print("Ending code.")
    
        time.sleep(.2)
        sys.exit()