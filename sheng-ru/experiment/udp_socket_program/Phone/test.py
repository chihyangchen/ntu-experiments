import socket
import time
import threading
import multiprocessing
import os
import sys
import datetime as dt
import argparse
import subprocess
import signal
from device_to_port import device_to_port

# adb_cmd = 'cd sdcard && ls'
su_cmd = 'iperf3 -s'
adb_cmd = f"su -c {su_cmd}"
# adb_cmd = 'ls'
p = subprocess.Popen([f'adb shell "{adb_cmd}"'], shell=True, preexec_fn = os.setpgrp)

# p = subprocess.call([f'adb shell {adb_cmd}'], shell=True, preexec_fn = os.setpgrp)
# p = subprocess.Popen(f'adb shell ls', shell=True, preexec_fn = os.setpgrp)


# time.sleep(.2)
# if p.poll() is None:
#     print('Finished!')


while True:
    try:
        
        time.sleep(1)
        print('Alive...')

    except KeyboardInterrupt:
        su_cmd = 'pkill iperf3'
        adb_cmd = f"su -c {su_cmd}"
        
        subprocess.Popen([f'adb shell "{adb_cmd}"'], shell=True)

        time.sleep(2)
        print('Finished!')
        sys.exit()