import subprocess
import argparse
import os
import time
import signal

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--devices", type=str, nargs='+', help="devices: e.g. sm00 qc00 qc02")
parser.add_argument("-b", "--baudrate", type=int, help='baudrate', default=9600)
args = parser.parse_args()

baudrate = args.baudrate
devs = args.devices

print('Monitoring...\n', devs)

miproc_list = []
for dev in devs:
    miproc = subprocess.Popen([f"python3 online_monitor.py -d {dev}"], shell=True, preexec_fn=os.setpgrp)
    miproc_list.append(miproc)

try:
    while True: time.sleep(60)
except:
    print('Killing mobileinsight process...')
    for miproc in miproc_list:
        os.killpg(os.getpgid(miproc.pid), signal.SIGINT)

