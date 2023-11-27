# Run Model with dual device bt multipleprocess
# Author: Sheng-Ru Zeng

import os, sys
import time
from threading import Timer
import multiprocessing
from multiprocessing import Process
import argparse
import json
import numpy as np
import datetime as dt

# Machine Learning Model
import xgboost as xgb
import catboost as cb

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MyAnalyzer

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

HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']

def get_array_features(analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in selected_features}

    return np.array(list(features.values()))

def show_HO(dev, analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'{dev}: HO {k} happened!!!!!')

def show_predictions(predictions):
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
    predictor = Predicter(rlf=rlf_classifier)

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
    
    # Threading Function
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
            try: f_out.write(','.join(w) + '\n')
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
    
    d2s_path = os.path.join(parent_folder, 'device_to_serial.json')
    with open(d2s_path, 'r') as f:
        device_to_serial = json.load(f)
        ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
        ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
        ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    print(dev1, dev2, ser1, ser2)
    
    # Record time
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
    
    # Read Coefficients
    time_seq = 20
    
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
    time.sleep(1)
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
                # show_predictions(dev1, out1)
                # show_predictions(dev2, out2)   
                
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