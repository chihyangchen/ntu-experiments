import os
import json
import datetime as dt
import time
import numpy as np
from threading import Timer
import datetime as dt

# Import MobileInsight modules
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import FeatureExtracter, MyMsgLogger

from .predictor import Predictor

def get_ser(folder, *dev):
    d2s_path = os.path.join(folder, 'device_to_serial.json')
    with open(d2s_path, 'r') as f:
        device_to_serial = json.load(f)
        return tuple(os.path.join("/dev/serial/by-id", f"usb-Quectel_RM500Q-GL_{device_to_serial[d]}-if00-port0") for d in dev)
    
# Show prediction result if event is predicted.
def show_predictions(dev, preds, thr = 0.5):
    
    if preds['rlf'] > thr:
        print(dt.datetime.now())
        print(f'{dev} Prediction: Near RLF!!!')

HOs = ['LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF']
def show_HO(dev, analyzer):

    features = analyzer.get_featuredict()
    features = {k: v for k, v in features.items() if k in HOs}
    
    for k, v in features.items():
        if v == 1:
            print(f'{dev}: HO {k} happened!!!!!')
            
selected_features = ['num_of_neis','RSRP', 'RSRQ', 'RSRP1','RSRQ1', 'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1','nr-RSRQ1', 
                     'E-UTRAN-eventA3', 'eventA5', 'NR-eventA3', 'eventB1-NR-r15',
                     'LTE_HO', 'MN_HO', 'SN_setup','SN_Rel', 'SN_HO', 'RLF', 'SCG_RLF',]
def get_array_features(analyzer):
    features = analyzer.get_featuredict()
    features = {k: features[k] for k in selected_features}

    return np.array(list(features.values()))

def class_far_close(preds1, preds2):
    
    case1, case2 = 'Far', 'Far'
    prob1, prob2 = 0, 0
    # t_close = 3 # Threshold time for tell if the radio is close to HO
    threshold = 0.5 # Threshold for binary cls model.
    
    for k in list(preds1.keys()):
        
        if k in ['rlf']:
            prob1 = preds1[k]
            prob2 = preds2[k]
            if preds1[k] > threshold:
                case1 = 'Close'
            
            if preds2[k] > threshold:
                case2 = 'Close'
            
    return case1, prob1, case2, prob2

# Online features collected and ML model inferring.
def device_running(dev, ser, baudrate, time_seq, time_slot, output_queue, start_sync_event, model_folder, SHOW_HO=False):
    
    # Loading Model
    rlf_classifier = os.path.join(model_folder, 'rlf_cls_xgb.json')
    predictor = Predictor(rlf = rlf_classifier)

    src = OnlineMonitor()
    src.set_serial_port(ser)  # the serial port to collect the traces
    src.set_baudrate(baudrate)  # the baudrate of the port
    # Record time for save filename
    now = dt.datetime.today()
    t = [str(x) for x in [now.year, now.month, now.day, now.hour, now.minute, now.second]]
    t = [x.zfill(2) for x in t]  # zero-padding to two digit
    t = '-'.join(t[:3]) + '_' + '-'.join(t[3:])
    
    save_path = os.path.join('/home/wmnlab/Data/mobileinsight', f"diag_log_{dev}_{t}.mi2log")
    src.save_log_as(save_path)
    
    dumper = MyMsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MyMsgLogger.XML) 
    dumper.set_dump_type(MyMsgLogger.FILE_ONLY)
    dumper.save_decoded_msg_as(f'/home/wmnlab/Data/XML/diag_log_{dev}_{t}.txt')
    
    feature_extracter = FeatureExtracter(mode='intensive')
    feature_extracter.set_source(src)

    save_path = os.path.join('/home/wmnlab/Data/record', f"record_{dev}_{t}.csv")
    f_out = open(save_path, 'w')
    f_out.write(','.join( ['Timestamp'] + selected_features + list(predictor.models.keys()) ) + '\n')
   
    # declare nonlocal
    l = int(1/time_slot)
    x_ins = [ [] for _ in range(l)]
    
    models_num = len(predictor.models)
    
    def run_prediction(i):
        
        nonlocal x_ins
        x_in = x_ins[i]
        
        start_time = dt.datetime.now()
        feature_extracter.gather_intensive_L()
        feature_extracter.to_featuredict()
        features = get_array_features(feature_extracter)
        if SHOW_HO and i == (l-1):
            show_HO(dev, feature_extracter)
        feature_extracter.remove_intensive_L_by_time(start_time - dt.timedelta(seconds=1-time_slot))
        feature_extracter.reset()

        if len(x_in) != (time_seq-1):
            
            x_in.append(features)
            if i == (l-1):
                print(f'{dev} {time_seq-len(x_in)} second after start...')

            # record
            w = [start_time.strftime("%Y-%m-%d %H:%M:%S.%f")] + [str(e) for e in list(features)]
            try: f_out.write(','.join(w + [''] * models_num) + '\n') 
            except: pass
            
        else:
            x_in.append(features)
            f_in = np.concatenate(x_in).flatten()
            out = predictor.foward(f_in)    
            x_in = x_in[1:]
            # record
            w = [start_time.strftime("%Y-%m-%d %H:%M:%S.%f")]+[str(e) for e in list(features) + list(out.values())]
            try: f_out.write(','.join(w) + ',\n')
            except: pass
            output_queue.put([dev, out, feature_extracter.cell_info])     

        x_ins[i] = x_in
        i = (i+1) % l
        Timer(time_slot, run_prediction, args=[i]).start()
    
    start_sync_event.wait()
    print(f'Start {dev}.')
    
    thread = Timer(time_slot, run_prediction, args=[0])
    thread.daemon = True
    thread.start()

    try:
        src.run()
    except:
        f_out.close()
        time.sleep(.5)
        print(f'End {dev}.')