import os
import sys
import subprocess
import time
from threading import Thread
import multiprocessing
from multiprocessing import Process
import signal
import datetime as dt
import argparse
import json
import re
# import pandas as pd
import numpy as np
import random

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

        names = ['LTE_HO', 'NR_HO', 'LTE_HO_time', 'NR_HO_time', 'NR_Setup', 'RLF']
        o1 = self.lte_clssifier.predict(x_in)
        o2 = self.nr_clssifier.predict(x_in)
        o3 = self.lte_forecaster.predict(x_in)
        o4 = self.nr_forecaster.predict(x_in)
        o5 = self.setup_clssifier.predict(x_in)
        o6 = self.rlf_clssifier.predict(x_in)
        
        out = [o1,o2,o3,o4,o5,o6]
        out = {k: v.item() for k, v in zip(names, out)}
        
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

# Change band function
def change_band(dev, band, variable_id):

    global setting1, setting2
    subprocess.Popen([f'./band-setting.sh -i {dev} -l {band}'], shell=True)

    if variable_id == 1:
        setting1 = band
        print(f"**********Change {dev} from {setting1} to {band}.**********")
    elif variable_id == 2:
        setting2 = band
        print(f"**********Change {dev} from {setting2} to {band}.**********")

# show
HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']

def show_HO(dev, analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'{dev} HO {k} happened!!!!!')

def show_predictions(predictions):

    thr = 0.5
    if predictions['LTE_HO'] > thr:
        v = predictions['LTE_HO_time']
        print(f'Prediction: {v} remaining LTE Ho happen!!!')
    if predictions['NR_HO'] > thr:
        v = predictions['NR_HO_time']
        print(f'Prediction: {v} remaining NR Ho happen!!!')
    if predictions['NR_Setup'] > thr:
        print(f'Prediction: Near NR setup!!!')
    if predictions['RLF'] > thr:
        print(f'Prediction: Near RLF!!!')


def happened_Events(preds1, preds2):

    evt1 = {'LTE_HO': None, 'NR_HO': None, 'NR_Setup': None, 'RLF': None}
    evt2 = {'LTE_HO': None, 'NR_HO': None, 'NR_Setup': None, 'RLF': None}
    
    thr = 0.5
    
    for preds, evt in zip([preds1, preds2], [evt1, evt2]):
        
        if preds['LTE_HO'] > thr:
            evt['LTE_HO'] = preds['LTE_HO_time']
            
        if preds['NR_HO'] > thr:
            evt['NR_HO'] = preds['NR_HO_time']
        
        if preds['NR_Setup'] > thr:
            evt['NR_Setup'] = 2
        
        if preds['RLF'] > thr:
            evt['RLF'] = 2    
    
    return evt1, evt2

from collections import namedtuple
import pandas as pd
import matplotlib.pyplot as plt

### Function
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

    global setting1, setting2
    choices = {'3:7', '7:8', '3:8'}
    choices1, choices2 = choices - set([setting1]), choices - set([setting2])
    choice1, choice2 = random.sample(choices1, 1), random.sample(choices2, 1)
    
    dl_thr, ul_thr = 0.5, 0.1
    
    if (eval_plr.dl > dl_thr):
        
        if (eval_plr1.dl > eval_plr2.dl):
            change_band(dev1, choice1, 1)
        else:
            change_band(dev2, choice2, 2)
    
    elif (eval_plr.ul > ul_thr):
        
        if (eval_plr1.ul > eval_plr2.ul):
            change_band(dev1, choice1, 1)
        else:
            change_band(dev2, choice2, 2)

# Online features collected.
def device_running(dev, ser, exc, output_queue, start_sync_event, sync_event, SHOW_HO=False):
    
    import xgboost as xgb

    # Loading Model
    lte_classifier = 'model/lte_HO_cls_xgb.json'
    nr_classifier = 'model/nr_HO_cls_xgb.json'
    lte_forecaster = 'model/lte_HO_fcst_xgb.json'
    nr_forecaster = 'model/nr_HO_fcst_xgb.json'
    setup_classifier = 'model/setup_cls_xgb.json'
    rlf_classifier = 'model/rlf_cls_xgb.json'
    predictor = Predicter(lte_classifier, nr_classifier, lte_forecaster, nr_forecaster, setup_classifier, rlf_classifier)

    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_dict_{dev}_{t}.mi2log")
    src.save_log_as(save_path)
    myanalyzer = MyAnalyzer()
    myanalyzer.set_source(src)

    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f"record_{dev}_{t}.txt")
    f_out = open(save_path, 'w')
    f_out.write(','.join(['LTE_HO, MN_HO', 'SN_setup', 'SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',
                          'num_of-neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1',
                          'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1',
                          'lte_cls','nr_cls','lte_fst','nr_fst','setup_cls','rlf_cls']) + '\n')
    
    def run_src():
        src.run()

    thread = Thread(target=run_src, daemon=True)
    thread.start()

    # For ML model running
    time.sleep(.5) # Clean time
    myanalyzer.reset() 

    start_sync_event.wait()
    print(f'Start {dev}.')
    count = 1

    try:
        while True:
            
            sync_event.wait()
            myanalyzer.to_featuredict()
            features = get_array_features(myanalyzer)

            if SHOW_HO:
                show_HO(dev, myanalyzer)

            if count <= time_seq:
                
                if count == 1: x_in = features
                else: x_in = np.concatenate((x_in, features), axis=0)

                print(f'{dev} {20-count} second after start...')

                count += 1

                # record
                w = [str(e) for e in list(features)]
                f_out.write(','.join(w + ['']*6) + ',\n') 
            
            else:
                
                x_in = np.concatenate((x_in[len(selected_features):], features), axis=0)
                x_in_D = xgb.DMatrix(x_in.reshape(1,-1))
                out = predictor.foward(x_in_D)
                
                # print(f'{dev}: {out}')

                # record
                w = [str(e) for e in list(features) + list(out.values())]
                f_out.write(','.join(w) + ',\n')

                output_queue.put([dev, out])

            myanalyzer.reset()
            sync_event.clear()

            if exc.is_set():
                raise KeyboardInterrupt

    except KeyboardInterrupt:

        f_out.close()
        time.sleep(1)
        print(f'End {dev}.')
        sys.exit()


if __name__ == "__main__":

    global setting1, setting2

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, nargs='+', help="device: e.g. qc00 qc01")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()
    baudrate = args.baudrate
    dev1, dev2 = args.device[0], args.device[1]

    with open('device_to_serial.json', 'r') as f:
        device_to_serial = json.load(f)
        ser1, ser2 = device_to_serial[dev1], device_to_serial[dev2]
        ser1 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser1}-if00-port0")
        ser2 = os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{ser2}-if00-port0")

    print(dev1, dev2, ser1, ser2)

    # Record time
    now = dt.datetime.today()
    t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])

    ### Read Coefficients
    time_seq = 20

    # Read Handover Profile
    coef_ul = pd.read_pickle('./HO_profiles/coef_ul.pkl')
    coef_dl = pd.read_pickle('./HO_profiles/coef_dl.pkl')

    # multipleprocessing
    output_queue = multiprocessing.Queue()
    start_sync_event = multiprocessing.Event()
    sync_event = multiprocessing.Event()

    exception1 = multiprocessing.Event()
    exception2 = multiprocessing.Event()

    time.sleep(.2)
    
    SHOW_HO = False
    p1 = Process(target=device_running, args=[dev1, ser1, exception1, output_queue, start_sync_event, sync_event, SHOW_HO])
    p1.start()    
    
    p2 = Process(target=device_running, args=[dev2, ser2, exception2, output_queue, start_sync_event, sync_event, SHOW_HO])
    p2.start()

        # cd modem-utilities to run code
    os.chdir("../../../modem-utilities/")
    setting1, setting2 = query_band(dev1), query_band(dev2)

    time.sleep(3)
    start_sync_event.set()
    time.sleep(.1)

    # Main Process
    try:

        while True: 
            
            start = time.time()
            sync_event.set()
            outs = {}
            
            while not output_queue.empty():
                dev_pres_pair = output_queue.get() 
                outs[dev_pres_pair[0]] = dev_pres_pair[1]
            
            if len(outs) == 2:

                out1 = outs[dev1]
                out2 = outs[dev2]
                ############ Action Here ##############

                # show_predictions(out1)
                # show_predictions(out2)
                evt1, evt2 = happened_Events(out1, out2)
                eval_plr, eval_plr1, eval_plr2 = evaluate_plr(evt1, evt2)
                # print(eval_plr, eval_plr1, eval_plr2)
                Action(eval_plr, eval_plr1, eval_plr2)

                #######################################

            end = time.time()
            time.sleep(1-(end-start))

    except KeyboardInterrupt:
        
        # Stop Record
        print('Main process received KeyboardInterrupt')
        exception1.set()
        exception2.set()

        p1.join()
        p2.join()

        time.sleep(1)
        print("Process killed, closed.")
    
        sys.exit()