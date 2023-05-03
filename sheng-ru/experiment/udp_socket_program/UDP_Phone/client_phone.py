#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime as dt
import os
import sys
import argparse
import subprocess
from device_to_port import device_to_port
from device_to_serial import device_to_serial

#=================argument parsing======================
parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", type=str,
                    help="server ip address", default="140.112.20.183")   # Lab249 外網
parser.add_argument("-d", "--devices", type=str, nargs='+',   # input list of devices sep by 'space'
                    help="list of devices", default=["unam"])
parser.add_argument("-p", "--ports", type=str, nargs='+',     # input list of port numbers sep by 'space'
                    help="ports to bind")
parser.add_argument("-b", "--bitrate", type=str,
                    help="target bitrate in bits/sec (0 for unlimited)", default="1M")
parser.add_argument("-l", "--length", type=str,
                    help="length of buffer to read or write in bytes (packet size)", default="250")
parser.add_argument("-t", "--time", type=int,
                    help="time in seconds to transmit for (default 1 hour = 3600 secs)", default=3600)
args = parser.parse_args()

devices = []
serials = []
for dev in args.devices:
    if '-' in dev:
        pmodel = dev[:2]
        start = int(dev[2:4])
        stop = int(dev[5:7]) + 1
        for i in range(start, stop):
            _dev = "{}{:02d}".format(pmodel, i)
            devices.append(_dev)
            serial = device_to_serial[_dev]
            serials.append(serial)
        continue
    devices.append(dev)
    serial = device_to_serial[dev]
    serials.append(serial)

ports = []
if not args.ports:
    for device in devices:
        # default uplink port and downlink port for each device
        ports.append((device_to_port[device][0], device_to_port[device][1]))  
else:
    for port in args.ports:
        if '-' in port:
            start = int(port[:port.find('-')])
            stop = int(port[port.find('-') + 1:]) + 1
            for i in range(start, stop):
                ports.append(i)
            continue
        ports.append(int(port))

print(devices)
print(serials)
print(ports)

#=================other variables========================
HOST = args.host # Lab 249
bitrate = args.bitrate
length = args.length
total_time = args.time
#=================global variables=======================

for device, port, serial in zip(devices, ports, serials):
    su_cmd = 'cd sdcard/UDP_Phone && python3 udp_socket_phone.py ' + \
            f'-H {HOST} -d {device} -p {port[0]} {port[1]} -b {bitrate} -l {length} -t {total_time}'
    adb_cmd = f"su -c '{su_cmd}'"
    p = subprocess.Popen([f'adb -s {serial} shell "{adb_cmd}"'], shell=True, preexec_fn = os.setpgrp)

try:

    while True:
        time.sleep(1)
        print('Alive...')

except KeyboardInterrupt:
    
    su_cmd = 'pkill -2 python3'
    adb_cmd = f"su -c '{su_cmd}'"
    for serial in serials:
        subprocess.Popen([f'adb -s {serial} shell "{adb_cmd}"'], shell=True)
    
    time.sleep(5)
    print('Closed main Process.')
    sys.exit()