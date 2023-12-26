# Run algorithm with dual device by multipleprocess
# Author: Sheng-Ru Zeng

import os
import sys
import subprocess
import time
from threading import Timer
import multiprocessing
from multiprocessing import Process
import datetime as dt
import argparse
import json
import re
import numpy as np
import random

# Machine Learning Model
import xgboost as xgb
import catboost as cb

# Import MobileInsight modules
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer, TimeSyncAnalyzer

# Predicter
class Predicter():

    def __init__(self, lte_cls=None, nr_cls=None, lte_fst=None, nr_fst=None, set_up=None, rlf=None):
        
        self.model_names = []
        self.file_names = []
        self.models = {}
        
        for name, file in zip(['lte_cls', 'nr_cls', 'lte_fst', 'nr_fst', 'set_up', 'rlf'], [lte_cls, nr_cls, lte_fst, nr_fst, set_up, rlf]):
            if file is None:
                continue
            self.model_names.append(name)
            self.file_names.append(file)
            # XGB Model 
            if file.endswith('.json'):
                self.models[name] = xgb.Booster()
                self.models[name].load_model(file)
            # Catboost Model
            elif file.endswith('cb'):
                if 'cls' in file:
                    self.models[name] = cb.CatBoostClassifier()
                    self.models[name].load_model(file)
                elif 'fcst' in file:
                    self.models[name] = cb.CatBoostRegressor()
                    self.models[name].load_model(file)
        
    def foward(self, x_in):
        
        out = {}
        for (name, model), file in zip(self.models.items(), self.file_names):
            if file is None:
                continue
            # XGB Model
            if file.endswith('.json'):
                x_in_D = xgb.DMatrix(x_in.reshape(1,-1))
                out[name] = model.predict(x_in_D)[0]
            # Catboost Model
            elif file.endswith('cb'):
                if 'cls' in file: # Classification
                    out[name] = model.predict_proba(x_in)[1]
                elif 'fcst' in file: # Regression
                    out[name] = model.predict(x_in)
        
        return out
    
# Query modem current band setting
def query_band(dev):

    out = subprocess.check_output(f'./band-setting.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    inds = [m.start() for m in re.finditer("lte_band", out)]
    inds2 = [m.start() for m in re.finditer("\r", out)]
    result = out[inds[1]+len('"lte_band"'):inds2[2]]
    print(f'Current Band Setting of {dev} is {result}')
    
    return result

selected_features = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                     'num_of_neis','RSRP', 'RSRQ', 'RSRP1','RSRQ1',
                     'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1','nr-RSRQ1']
def get_array_features(analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in selected_features}

    return np.array(list(features.values()))

HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']
def show_HO(dev, analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'{dev}: HO {k} happened!!!!!')

# Online features collected and ML model inferring.
def device_running(dev, ser, output_queue, start_sync_event, SHOW_HO=False):
    
    # Loading Model
    # lte_classifier = os.path.join(parent_folder, 'model/lte_HO_cls_xgb.json')
    # nr_classifier = os.path.join(parent_folder, 'model/nr_HO_cls_cb')
    # lte_forecaster = os.path.join(parent_folder, 'model/lte_HO_fcst_xgb.json')
    # nr_forecaster = os.path.join(parent_folder, 'model/nr_HO_fcst_cb')
    # setup_classifier = os.path.join(parent_folder, 'model/setup_cls_xgb.json')
    rlf_classifier = os.path.join(parent_folder, 'model/rlf_cls_xgb.json')
    predictor = Predicter(rlf = rlf_classifier)

    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(save_path)
    myanalyzer = MyAnalyzer()
    myanalyzer.set_source(src)
    
    save_path = f'/home/wmnlab/Data/TimeSync/TimeSync_{dev}_{t}.csv'
    timesyncanalyzer = TimeSyncAnalyzer(save_path=save_path)
    timesyncanalyzer.set_source(src)

    save_path = os.path.join('/home/wmnlab/Data/record', f"record_{dev}_{t}.csv")
    f_out = open(save_path, 'w')
    f_out.write(','.join(['LTE_HO, MN_HO', 'SN_setup', 'SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                          'num_of-neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1',
                          'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1'] +
                          list(predictor.models.keys()) ) + '\n')
   
    global count, x_in
    count = 1
    x_in = np.array([])
    
    models_num = len(predictor.models)
    
    def run_prediction():
        
        global count, x_in

        myanalyzer.to_featuredict()
        features = get_array_features(myanalyzer)

        if SHOW_HO:
            show_HO(dev, myanalyzer)
            
        myanalyzer.reset()

        if count <= time_seq:
            
            if count == 1: x_in = features
            else: x_in = np.concatenate((x_in, features), axis=0)

            print(f'{dev} {20-count} second after start...')

            count += 1

            # record
            w = [str(e) for e in list(features)]
            try: f_out.write(','.join(w + [''] * models_num) + '\n') 
            except: pass
            
        else:
            
            x_in = np.concatenate((x_in[len(selected_features):], features), axis=0)
            out = predictor.foward(x_in)    
        
            # record
            w = [str(e) for e in list(features) + list(out.values())]
            try: f_out.write(','.join(w) + ',\n')
            except: pass
            output_queue.put([dev, out])     

        Timer(1, run_prediction).start()
    
    start_sync_event.wait()
    print(f'Start {dev}.')
    
    thread = Timer(1, run_prediction)
    thread.daemon = True
    thread.start()

    try:
        src.run()
    except:
        f_out.close()
        time.sleep(.5)
        print(f'End {dev}.')

# Show prediction result if event is predicted.
def show_predictions(dev, preds):
    
    thr = 0.2
    if preds['rlf'] > thr:
        print(dt.datetime.now())
        print(f'{dev} Prediction: Near RLF!!!')

# This function determine 
# remain_time_for_cls_model = 2
def class_far_close(preds1, preds2):
    
    case1, case2 = 'Far', 'Far'
    prob1, prob2 = 0, 0
    # t_close = 3 # Threshold time for tell if the radio is close to HO
    threshold = 0.2 # Threshold for binary cls model.
    
    for k in list(preds1.keys()):
        
        if k in ['rlf']:
            prob1 = preds1[k]
            prob2 = preds2[k]
            if preds1[k] > threshold:
                case1 = 'Close'
            
            if preds2[k] > threshold:
                case2 = 'Close'
            
    return case1, prob1, case2, prob2

# Use AT command to query modem current serving pci, earfcn
def query_pci_earfcn(dev):

    out = subprocess.check_output(f'./get-pci-freq.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    out = out.split('\n')
    
    if len(out) == 7: # ENDC Mode
        lte_info = out[2].split(',')
        nr_info = out[3].split(',')
        pci, earfcn, band = lte_info[5], lte_info[6], lte_info[7]
        nr_pci = nr_info[3]
        return (pci, earfcn, band, nr_pci)
    elif len(out) == 5: # LTE Mode
        lte_info = out[1].split(',')
        pci, earfcn, band = lte_info[7], lte_info[8], lte_info[9]
        return (pci, earfcn, band)

# Change band function
def change_band(dev, band, variable_id):

    global setting1, setting2, rest
    subprocess.Popen([f'./band-setting.sh -i {dev} -l {band}'], shell=True)

    if variable_id == 1:
        print(f"**********Change {dev} from {setting1} to {band}.**********")
        setting1 = band
    elif variable_id == 2:
        print(f"**********Change {dev} from {setting2} to {band}.**********")
        setting2 = band
        
    rest = rest_time
    
if __name__ == "__main__":
    
    script_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(script_folder)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, nargs='+', help="device: e.g. qc00 qc01")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()
    baudrate = args.baudrate
    dev1, dev2 = args.device[0], args.device[1]
    
    # global parameters and some other parameters
    current_script_path = os.path.abspath(__file__)
    dir_name = os.path.dirname(current_script_path)
    for i in range(4):
        dir_name = os.path.dirname(dir_name)
    dir_name = os.path.join(dir_name, 'modem-utilities')
    os.chdir(dir_name) # cd modem-utilities folder to use AT command.
    
    global setting1, setting2, rest
    setting1, setting2 = query_band(dev1), query_band(dev2)
    time_seq = 20 ### Read Coefficients
    rest = 0
    rest_time = 10
    all_band_choice = [ '3', '7', '8', '1:3:7:8', 
                       '1:3', '3:7', '3:8', '7:8', '1:7', '1:8',
                       '1:3:7', '1:3:8', '1:7:8', '3:7:8']

    d2s_path = os.path.join(parent_folder, 'device_to_serial.json')
    with open(d2s_path, 'r') as f:
        device_to_serial = json.load(f)
        ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
        ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
        ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    print(dev1, dev2, ser1, ser2)
    
    # Record time for save filename
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year, now.month, f'{now.day}_{now.hour}', now.minute, now.second]])
    
    # multipleprocessing
    output_queue = multiprocessing.Queue()
    start_sync_event = multiprocessing.Event()
    
    time.sleep(.2)
    SHOW_HO = True
    
    p1 = Process(target=device_running, args=[dev1, ser1, output_queue, start_sync_event, SHOW_HO])
    p1.start()    
    
    p2 = Process(target=device_running, args=[dev2, ser2, output_queue, start_sync_event, SHOW_HO])
    p2.start()
    
    # Sync two device.
    time.sleep(3)
    start_sync_event.set()
    time.sleep(.1)
    
    # Main Process
    try:

        while True: 
            
            start = time.time()
            outs = {}
            
            while not output_queue.empty():
                dev_pres_pair = output_queue.get() 
                outs[dev_pres_pair[0]] = dev_pres_pair[1]
    
            if len(outs) == 2:
                
                out1 = outs[dev1]
                out2 = outs[dev2]

                # Show prediction result during experiment. 
                show_predictions(dev1, out1); show_predictions(dev2, out2)
                
                ################ Action Here ################
                # Do nothing if too close to previous action.
                if rest > 0:
                    rest -= 1
                    print(f'Rest for {rest} more second.')
                else:
                    
                    case1, prob1, case2, prob2 = class_far_close(out1, out2) 
                    
                    # Format of info: (pci, earfcn, band, nr_pci) under 5G NSA; # (pci, earfcn, band) under LTE
                    try:
                        info1, info2 = query_pci_earfcn(dev1), query_pci_earfcn(dev2)
                        if info1 is None or info2 is None: raise
                    except:
                        print('Query Failed.')
                        end = time.time()
                        if 1-(end-start) > 0:
                            time.sleep(1-(end-start))
                        continue
                    
                    if case1 == 'Far' and case2 == 'Far':
                        # if info1[0] == info2[0]: # Same PCI
                        #     choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                        #     choice =  random.sample(choices, 1)[0]
                        #     print('Case Same PCI!!!')
                        #     # Change in turn
                        #     try: chx += 1
                        #     except: chx = 0
                        #     if chx % 2 == 0:
                        #         change_band(dev2, choice, 2)
                        #     else:
                        #         change_band(dev1, choice, 1)
                        
                        pass # Fine, let's pass first.
                    
                    elif case1 == 'Far' and case2 == 'Close':
                        if info1[0] == info2[0]: # Same PCI
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print(f'{dev1} far but {dev2} close and same PCI!!!')
                            change_band(dev2, choice, 2)
                            
                    elif case1 == 'Close' and case2 == 'Far':
                        if info1[0] == info2[0]: # Same PCI
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print(f'{dev2} far but {dev1} close and same PCI!!!')
                            change_band(dev1, choice, 1)
                            
                    elif case1 == 'Close' and case2 == 'Close':
                        choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                        choice =  random.sample(choices, 1)[0]
                        print(f'2 close')
                        if prob1 > prob2:
                            change_band(dev1, choice, 1)
                        else:
                            change_band(dev2, choice, 2)   
                #############################################
                
            end = time.time()
            if 1-(end-start) > 0:
                time.sleep(1-(end-start))

        
    except KeyboardInterrupt:
        
        # Stop Record
        print('Main process received KeyboardInterrupt')
        
        p1.join()
        p2.join()

        time.sleep(1)
        print("Process killed, closed.")
    
        sys.exit()