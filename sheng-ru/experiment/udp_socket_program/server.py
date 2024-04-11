#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

#=================argument parsing======================
parser = argparse.ArgumentParser() 
parser.add_argument("-s", "--server_ip", type=str, help="server ip", default='0.0.0.0') 
parser.add_argument("-n", "--number_client", type=int, help="number of client", default=1)
parser.add_argument("-d", "--devices", type=str, nargs='+', required=True, help="list of devices", default=["unam"])
parser.add_argument("-p", "--ports", type=str, nargs='+', help="ports to bind")
parser.add_argument("-b", "--bitrate", type=str, help="target bitrate in bits/sec (0 for unlimited)", default="1M")
parser.add_argument("-l", "--length", type=str, help="length of buffer to read or write in bytes (packet size)", default="250")
parser.add_argument("-t", "--time", type=int, help="time in seconds to transmit for (default 1 hour = 3600 secs)", default=3600)
args = parser.parse_args()

# Get argument devices
devices = []
for dev in args.devices:
    if '-' in dev:
        pmodel = dev[:2]
        start = int(dev[2:4])
        stop = int(dev[5:7]) + 1
        for i in range(start, stop):
            _dev = "{}{:02d}".format(pmodel, i)
            devices.append(_dev)
        continue
    devices.append(dev)

# Get the corresponding ports with devices
ports = []
if not args.ports:
    for device in devices:
        # default uplink port and downlink port for each device
        ports.append((device_to_port[device][0], device_to_port[device][1]))  
else:
    for port in args.ports:
        ports.append([int(port), int(port)+1])

print(devices)
print(ports)

length_packet = int(args.length)

if args.bitrate[-1] == 'k':
    bandwidth = int(args.bitrate[:-1]) * 1e3
elif args.bitrate[-1] == 'M':
    bandwidth = int(args.bitrate[:-1]) * 1e6
else:
    bandwidth = int(args.bitrate)

print("bitrate:", bandwidth)

total_time = args.time

number_client = args.number_client

expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec

# global variables
HOST = args.server_ip
stop_threads = False
udp_addr = {}

# Function define
def signal_handler(signum, frame):

    print("Inner Signal: ",signum)

    data = 'CLOSE'
    conn.send(data.encode())
    
    global stop_threads
    stop_threads = True

    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin subprocess
    sync_proc.terminate()
    print("time sync socket closed")

    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

    exit(0)

def fill_udp_addr(s):

    _, addr = s.recvfrom(1024)
    udp_addr[s] = addr 

def receive(s, dev, port):

    global stop_threads
    print(f"wait for indata from {dev} at {port}...")

    seq = 1
    prev_receive = 1
    time_slot = 1

    while not stop_threads:
        try:
            #receive data
            indata, _ = s.recvfrom(1024)
           
            try: start_time
            except NameError:
                start_time = time.time()

            if len(indata) != length_packet:
                print("packet with strange length: ", len(indata))

            seq = int(indata.hex()[32:40], 16)
            ts = int(int(indata.hex()[16:24], 16)) + float("0." + str(int(indata.hex()[24:32], 16)))

            # Show information
            if time.time()-start_time > time_slot:
                print(f"{dev}:{port} [{time_slot-1}-{time_slot}]", "receive", seq-prev_receive)
                time_slot += 1
                prev_receive = seq

        except Exception as inst:
            print("Error: ", inst)
            stop_threads = True

def transmit(sockets):

    global stop_threads
    print("start transmission: ")
    
    seq = 1
    prev_transmit = 0
    
    start_time = time.time()
    next_transmit_time = start_time + sleeptime
    
    time_slot = 1
    
    while time.time() - start_time < total_time and not stop_threads:
        try:
            t = time.time()
            while t < next_transmit_time:
                t = time.time()
            next_transmit_time = next_transmit_time + sleeptime

            euler = 271828
            pi = 31415926
            datetimedec = int(t)
            microsec = int((t - int(t))*1000000)

            redundant = os.urandom(length_packet-4*5)
            outdata = euler.to_bytes(4, 'big') + pi.to_bytes(4, 'big') + datetimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant
            
            for s in sockets:
                if s in udp_addr.keys():
                    s.sendto(outdata, udp_addr[s])
            seq += 1
        
            if time.time()-start_time > time_slot:
                print("[%d-%d]"%(time_slot-1, time_slot), "transmit", seq-prev_transmit)
                time_slot += 1
                prev_transmit = seq

        except Exception as e:
            print(e)
            stop_threads = True
    stop_threads = True
    print("---transmission timeout---")
    print("transmit", seq, "packets")

# open subprocess of time synchronizatoin
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(dir_path, "time_sync.py")
sync_proc =  subprocess.Popen([f"exec python3 {file_path} -s"], shell=True, preexec_fn = os.setpgrp)

# TCP control socket
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_tcp.bind((HOST, 3299))
s_tcp.listen(5)
print('wait for TCP connection...')
conn, addr = s_tcp.accept()
print('connected by ' + str(addr))
time.sleep(1)

# Set up UL receive /  DL transmit sockets for multiple clients
rx_sockets = []
tx_sockets = []
for dev, port in zip(devices, ports):
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.bind((HOST, port[0]))
    rx_sockets.append(s1)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2.bind((HOST, port[1]))
    tx_sockets.append(s2)
    print(f'Create socket at {HOST}:{port[0]} for UL...')
    print(f'Create socket at {HOST}:{port[1]} for DL...')

# Get client addr with server DL port first
t_fills = []
for s in tx_sockets:
    t = threading.Thread(target=fill_udp_addr, args=(s, ))
    t.start()
    t_fills.append(t)

print('Wait for filling up client address first...')
for t in t_fills:
    t.join()
print('Successful get udp addr!')

# Start subprocess of tcpdump
now = dt.datetime.today()
n = [str(x) for x in [now.year, now.month, now.day, now.hour, now.minute, now.second]]
n = [x.zfill(2) for x in n]  # zero-padding to two digit
n = '-'.join(n[:3]) + '_' + '-'.join(n[3:])
pcap_path = '/home/wmnlab/temp'

tcpproc_list = []
for device, port in zip(devices, ports):
    pcap = os.path.join(pcap_path, f"server_pcap_BL_{device}_{port[0]}_{port[1]}_{n}_sock.pcap")
    tcpproc =  subprocess.Popen([f"sudo tcpdump -i any port '({port[0]} or {port[1]})' -w {pcap}"], shell=True, preexec_fn = os.setpgrp)
    tcpproc_list.append(tcpproc)    
time.sleep(1)

# Create and start UL receive multi-thread

rx_threads = []
for s, dev, port in zip(rx_sockets, devices, ports):
    t_rx = threading.Thread(target = receive, args=(s, dev, port[0]), daemon=True)
    rx_threads.append(t_rx)
    t_rx.start()

# Start DL transmission multipleprocessing
p_tx = multiprocessing.Process(target=transmit, args=(tx_sockets,), daemon=True)
p_tx.start()

# Main process waiting...
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)

try:
    
    indata = conn.recv(1024)
    print('received ' + indata.decode() + ' command from client')

    stop_threads = True
    
    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin subprocess
    sync_proc.terminate()
    print("time sync socket closed")

    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

except SystemExit as e: print('Successfully closed.')
except BaseException as e:

    print(e)

    stop_threads = True
    data = 'CLOSE'
    conn.send(data.encode())
    
    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin subprocess
    sync_proc.terminate()
    # os.killpg(os.getpgid(sync_proc.pid), signal.SIGINT)
    print("time sync socket closed")
    
    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

    print('Error, Closed.')