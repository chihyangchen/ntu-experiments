# Run algorithm with dual device by multipleprocess
# Author: Sheng-Ru Zeng
import os
import sys
import time

import multiprocessing
from multiprocessing import Process
import argparse
import random

from myutils.at_commands import AT_Cmd_Runner
from myutils.functions import *

if __name__ == "__main__":
    
    script_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(script_folder)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, nargs='+', help="device: e.g. qc00 qc01")
    parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
    args = parser.parse_args()
    baudrate = args.baudrate
    dev1, dev2 = args.device[0], args.device[1]
    ser1, ser2 = get_ser(parent_folder, *[dev1, dev2])
    
    at_cmd_runner = AT_Cmd_Runner()
    os.chdir(at_cmd_runner.dir_name) # cd modem utils dir to run atcmd
    
    # global variable
    setting1, setting2 = at_cmd_runner.query_band(dev1), at_cmd_runner.query_band(dev2)
    rest = 0
    rest_time = 10
    time_seq = 10 # Read Coefficients
    
    all_band_choice1 = [ '3', '7', '1:3:7:8', '1:3', '3:7', '3:8', '7:8', '1:7',
                        '1:3:7', '1:3:8', '1:7:8', '3:7:8']
    all_band_choice2 = [ '3', '7', '8', '1:3:7:8', '1:3', '3:7', '3:8', '7:8', '1:7', '1:8',
                        '1:3:7', '1:3:8', '1:7:8', '3:7:8']
    
    # multipleprocessing
    output_queue = multiprocessing.Queue()
    start_sync_event = multiprocessing.Event()
    time.sleep(.2)
    
    SHOW_HO = True
    model_folder = os.path.join(parent_folder, 'model')
    
    p1 = Process(target=device_running, args=[dev1, ser1, baudrate, time_seq, output_queue, start_sync_event, model_folder, SHOW_HO])     
    p2 = Process(target=device_running, args=[dev2, ser2, baudrate, time_seq, output_queue, start_sync_event, model_folder, SHOW_HO])
    p1.start()
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
                        info1, info2 = at_cmd_runner.query_pci_earfcn(dev1), at_cmd_runner.query_pci_earfcn(dev2)
                        if info1 is None or info2 is None: raise
                        info1_, info2_ = info1, info2
                    except:
                        print('Query Failed. Use previous one.')
                        info1, info2 = info1_, info2_
                    
                    if case1 == 'Far' and case2 == 'Far':
                        pass # Fine, let's pass first.
                    
                    elif case1 == 'Far' and case2 == 'Close':
                        choices = all_band_choice2
                        choice =  random.sample(choices, 1)[0]
                        print(f'{dev1} far but {dev2} close!!!')
                        at_cmd_runner.change_band(dev2, choice, setting2)
                        setting2, rest = choice, rest_time
                            
                    elif case1 == 'Close' and case2 == 'Far':
                        choices = all_band_choice1
                        choice =  random.sample(choices, 1)[0]
                        print(f'{dev2} far but {dev1} close!!!')
                        at_cmd_runner.change_band(dev1, choice, setting1) 
                        setting1, rest = choice, rest_time
                            
                    elif case1 == 'Close' and case2 == 'Close':
                        choices = all_band_choice2
                        choice =  random.sample(choices, 1)[0]
                        print(f'R1/R2 both close')
                        at_cmd_runner.change_band(dev2, choice, setting2)
                        setting2, rest = choice, rest_time # change dev2 
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