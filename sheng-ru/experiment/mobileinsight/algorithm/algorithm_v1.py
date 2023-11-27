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
from mobile_insight.analyzer import MyAnalyzer

# HO profile needing
from collections import namedtuple
import pandas as pd
import matplotlib.pyplot as plt

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
    print(f'Current Band Setting of {dev} is {result}')
    
    return result

# Use AT command to
# Query modem current serving pci, earfcn
def query_pci_earfcn(dev):

    out = subprocess.check_output(f'./get-pci-freq.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    lte_info = out.split('\n')[2]
    nr_info = out.split('\n')[3]
    pci, earfcn, band = lte_info.split(',')[5], lte_info.split(',')[6], lte_info.split(',')[7]
    nr_pci = nr_info.split(',')[3]
    
    return pci, earfcn, band, nr_pci
   
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

# show
HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']
def show_HO(dev, analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'{dev}: HO {k} happened!!!!!')

def show_predictions(dev, preds):
    
    thr = 0.5
    if preds['lte_cls'] > thr:
        v = preds['lte_fst']
        print(f'{dev} Prediction: {v} remaining LTE Ho happen!!!')
    if preds['nr_cls'] > thr:
        v = preds['nr_fst']
        print(f'{dev} Prediction: {v} remaining NR Ho happen!!!')
    if preds['set_up'] > thr:
        print(f'{dev} Prediction: Near NR setup!!!')
    if preds['rlf'] > thr:
        print(f'{dev} Prediction: Near RLF!!!')

remain_time_for_cls_model = 2

# Useful function for action design.
def happened_Events(preds1, preds2):
    
    evt1 = {'LTE_HO': None, 'NR_HO': None, 'NR_Setup': None, 'RLF': None}
    evt2 = {'LTE_HO': None, 'NR_HO': None, 'NR_Setup': None, 'RLF': None}
    
    thr = 0.5
    
    for preds, evt in zip([preds1, preds2], [evt1, evt2]):
        
        if preds['lte_cls'] > thr:
            evt['LTE_HO'] = preds['lte_fst']
            
        if preds['nr_cls'] > thr:
            evt['NR_HO'] = preds['nr_fst']
        
        if preds['set_up'] > thr:
            evt['NR_Setup'] = remain_time_for_cls_model
        
        if preds['rlf'] > thr:
            evt['RLF'] = remain_time_for_cls_model    
    
    return evt1, evt2

# Classification case 'Far' from HO or 'Close' from HO.
# This function input the output from function happened event and
# output the classification of the radio is near or far from a HO. 
def class_far_close(evt1, evt2):

    cls_result = []
    remain_time1, remain_time2 = [], [] 
    threshold = 3 # Threshold for tell if the radio is close to HO
     
    for evt, remain_time in zip([evt1, evt2], [remain_time1, remain_time2]):
    
        if evt['NR_Setup'] is not None:
            remain_time.append(remain_time_for_cls_model)
            
        if evt['RLF'] is not None:    
            remain_time.append(remain_time_for_cls_model)
            
        if evt['LTE_HO'] is not None:
            remain_time.append(evt['LTE_HO'])
            
        if evt['NR_HO'] is not None:
            remain_time.append(evt['NR_HO'])
            
        if len(remain_time) == 0 or all(t < threshold for t in remain_time):
            cls_result.append('Far')
        else:
            cls_result.append('Close')
            
    return (cls_result[0], remain_time1, cls_result[1], remain_time2)

def check_difference_less_than_off(list_a, list_b, off):
    if not list_a or not list_b:  
        return False
    for a in list_a:
        for b in list_b:
            if abs(a - b) < off:
                return True
    return False

def evaluate_plr(radio1, radio2, predict_time=10, spr=500, show_fig=False):
    
    def heaviside(x, left, right):
    
        if x < left:
            return 0
        elif x > right:
            return 0
        else:
            return 1

    def poly_approx(x_list, type, center=0, mode='ul'):
        
        if center == None:
            p = np.poly1d(0)
            return p(x_list)
        
        if mode == 'ul':
            _coef = list(coef_ul.loc[type])
        else: # mode == 'dl'
            _coef = list(coef_dl.loc[type])
            
        x_list = [x - center for x in x_list]
        lower_bd = _coef[0]
        upper_bd = _coef[1]
        coef = _coef[2:]
        p = np.poly1d(coef)
        
        return np.clip(p(x_list)*np.vectorize(heaviside)(x_list, lower_bd, upper_bd), a_min=0, a_max=100)
    
    OP = namedtuple('Output', 'ul, dl', defaults=(None, None))
    
    eval_plr = []
    eval_plr1 = []
    eval_plr2 = []
    
    x = [s/spr for s in list(range(1, predict_time * spr + 1))]
    for mode in ['ul', 'dl']:
        Y1 = []
        Y2 = []
        for tag in ['LTE_HO', 'NR_HO', 'RLF', 'NR_Setup']:
            y1 = poly_approx(x, 'NR_HO', center=radio1[tag], mode=mode)
            y2 = poly_approx(x, 'RLF', center=radio2[tag], mode=mode)
            Y1.append(y1)
            Y2.append(y2)
        y1 = [s1+s2+s3+s4 if s1+s2+s3+s4 <= 100 else 100 for (s1, s2, s3, s4) in zip(Y1[0],Y1[1],Y1[2],Y1[3])]
        y2 = [s1+s2+s3+s4 if s1+s2+s3+s4 <= 100 else 100 for (s1, s2, s3, s4) in zip(Y2[0],Y2[1],Y2[2],Y2[3])]
        y = [s1*s2/100 for (s1, s2) in zip(y1, y2)]
        eval_plr.append(round(np.mean(y), 2))
        eval_plr1.append(round(np.mean(y1), 2))
        eval_plr2.append(round(np.mean(y2), 2))

        if show_fig:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x, y, '-', c='tab:orange', lw=0.5)
            ax.fill_between(x, y, color='tab:orange', alpha=0.3)
            ax.set_xlabel('Time (sec)')
            ax.set_ylabel('Evaluated PLR (%)')
            if mode == 'ul':
                ax.set_title('Uplink')
            else:    
                ax.set_title('Downlink')

    return OP(eval_plr[0], eval_plr[1]), OP(eval_plr1[0], eval_plr1[1]), OP(eval_plr2[0], eval_plr2[1])

def Action(eval_plr, eval_plr1, eval_plr2):
    pass
    
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
    os.chdir("../../../../modem-utilities/") # cd modem-utilities folder to use AT command.
    global setting1, setting2, rest
    setting1, setting2 = query_band(dev1), query_band(dev2)
    time_seq = 20     ### Read Coefficients
    rest = 0
    rest_time = 5
    offset_too_close = 1
    offset_eval = 0.05
    all_band_choice = [ '3', '7', '8', '1:3:7:8', 
                       '1:3', '3:7', '3:8', '7:8', '1:7', '1:8',
                       '1:3:7', '1:3:8', '1:7:8', '3:7:8']
    radical = False
    
    d2s_path = os.path.join(parent_folder, 'device_to_serial.json')
    with open(d2s_path, 'r') as f:
        device_to_serial = json.load(f)
        ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
        ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
        ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    print(dev1, dev2, ser1, ser2)
    
    # Record time for save file name
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])

    
    # # Read Handover Profile
    coef_ul = pd.read_pickle(os.path.join(parent_folder, 'data/coef_ul.pkl'))
    coef_dl = pd.read_pickle(os.path.join(parent_folder, 'data/coef_dl.pkl'))

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
                # show_predictions(dev1, out1); show_predictions(dev2, out2)
                
                ################ Action Here ################
                # Do nothing if too close to previous action.
                if rest > 0:
                    rest -= 1
                    print(f'Rest for {rest} more second.')
                else:
                    
                    evt1, evt2 = happened_Events(out1, out2)
                    case1, remain_time1, case2, remain_time2 = class_far_close(evt1, evt2)    
                    # Format of info: (pci, earfcn, band, nr_pci) under 5G NSA
                    try:
                        info1, info2 = query_pci_earfcn(dev1), query_pci_earfcn(dev2)
                    except:
                        end = time.time()
                        if 1-(end-start) > 0:
                            time.sleep(1-(end-start))
                        continue
                    
                    
                    if case1 == 'Far' and case2 == 'Far':
                        
                        # To check if dev1 and dev2 have same pci,
                        # if so, try other band.
                        if info1[0] == info2[0]:
                            
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print('Case Same PCI!!!')
                            try: chx += 1
                            except: chx = 0
                            if chx % 2 == 0:
                                change_band(dev2, choice, 2)
                            else:
                                change_band(dev1, choice, 1)
                                
                    elif case1 == 'Close' and case2 == 'Far':
                    
                        # To check if two event is too close.
                        if check_difference_less_than_off(remain_time1, remain_time2, offset_too_close):
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print('Case 1 close 2 far!!!')
                            change_band(dev1, choice, 1)
                    
                    elif case1 == 'Far' and case2 == 'Close':
                    
                        # Do if radical = True
                        if radical:
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            change_band(dev2, choice, 2)
                            
                        # To check if two event is too close.
                        elif check_difference_less_than_off(remain_time1, remain_time2, offset_too_close):
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print('Case 2 close 1 far!!!')
                            change_band(dev2, choice, 2)
                    
                    elif case1 == 'Close' and case2 == 'Close':
                        
                        _, eval_plr1, eval_plr2 = evaluate_plr(evt1, evt2)
                        
                        # If event severety too close, change the earlier one.
                        if abs(eval_plr1.dl - eval_plr2.dl) < offset_eval:
                            
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            
                            if min(remain_time1) < min(remain_time2):
                                print('Case 2 very close 1 change!!!')
                                change_band(dev1, choice, 1)
                            else:
                                print('Case 2 very close 2 change!!!')
                                change_band(dev2, choice, 2)
                        
                        elif eval_plr1.dl > eval_plr2.dl:
                            
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]
                            print('Case 2 close 1 change!!!')
                            change_band(dev1, choice, 1)
                            
                        elif eval_plr1.dl < eval_plr2.dl:
                            
                            choices = [c for c in all_band_choice if (info1[2] not in c and info2[2] not in c)] 
                            choice =  random.sample(choices, 1)[0]       
                            print('Case 2 close 2 change!!!')
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