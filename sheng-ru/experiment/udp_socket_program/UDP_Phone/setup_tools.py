import argparse
from device_to_serial import device_to_serial
import subprocess
import time
import os

#=================argument parsing======================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device", type=str,   
                    help="device", default=["unam"])
args = parser.parse_args()
device = args.device

serial = device_to_serial[device]

su_cmd = 'cd sdcard/UDP_Phone && cp ./tools/* /bin && chmod +x /bin/*'
adb_cmd = f"su -c '{su_cmd}'"
p = subprocess.Popen([f'adb -s {serial} shell "{adb_cmd}"'], shell=True, preexec_fn = os.setpgrp)
time.sleep(1)
su_cmd = 'chmod +x /bin/*'
adb_cmd = f"su -c '{su_cmd}'"
p = subprocess.Popen([f'adb -s {serial} shell "{adb_cmd}"'], shell=True, preexec_fn = os.setpgrp)
time.sleep(1)
