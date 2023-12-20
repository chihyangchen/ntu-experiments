#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import time
import threading
import multiprocessing
import datetime as dt
import os
import argparse
import subprocess
import signal
from device_to_port import device_to_port

#=================argument parsing======================
parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", type=str, help="server ip address", default="140.112.20.183")   # Lab249 外網
parser.add_argument("-d", "--devices", type=str, nargs='+', required=True, help="list of devices", default=["unam"])
parser.add_argument("-p", "--ports", type=str, nargs='+', help="ports to bind")
parser.add_argument("-b", "--bitrate", type=str, help="target bitrate in bits/sec (0 for unlimited)", default="1M")
parser.add_argument("-l", "--length", type=str, help="length of buffer to read or write in bytes (packet size)", default="250")
parser.add_argument("-t", "--time", type=int, help="time in seconds to transmit for (default 1 hour = 3600 secs)", default=3600)
parser.add_argument("-w", "--file", type=str, help="time synchronization save filename")

args = parser.parse_args()

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

expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec

# Start subprocess of tcpdump
now = dt.datetime.today()
n = [str(x) for x in [now.year, now.month, now.day, now.hour, now.minute, now.second]]
n = [x.zfill(2) for x in n]  # zero-padding to two digit
n = '-'.join(n[:3]) + '_' + '-'.join(n[3:])

if args.file:
    syncfile = args.file
else:
    syncfile = f'/home/wmnlab/temp/time_sync_{n}.json'

# global variables
HOST = args.host
stop_threads = False

# Function define
def signal_handler(signum, frame):

    print("Inner Signal: ",signum)

    outdata = 'CLOSE'
    s_tcp.send(outdata.encode())

    global stop_threads
    stop_threads = True

    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin process
    p_sync.terminate()
    print("regular time sync process closed")

    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

    exit(0)

def give_server_DL_addr():
    
    for s, port in zip(rx_sockets, ports):
        outdata = 'hello'
        s.sendto(outdata.encode(), (HOST, port[1]))

def receive(s, dev):

    global stop_threads
    print(f"wait for indata to {dev} from server...")

    seq = 1
    prev_receive = 1
    time_slot = 1

    while not stop_threads:
        try:

            indata, addr = s.recvfrom(1024)

            try: start_time
            except NameError:
                start_time = time.time()

            if len(indata) != length_packet:
                print("packet with strange length: ", len(indata))

            seq = int(indata.hex()[32:40], 16)
            ts = int(int(indata.hex()[16:24], 16)) + float("0." + str(int(indata.hex()[24:32], 16)))

            # Show information
            if time.time()-start_time > time_slot:
                print(f"{dev} [{time_slot-1}-{time_slot}]", "receive", seq-prev_receive)
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
            
            for s, port in zip(sockets, ports):     
                s.sendto(outdata, (HOST, port[0]))
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

def regular_time_sync():
    interval_minutes = 20
    while True:
        try:
            dir_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(dir_path, "time_sync.py")
            subprocess.Popen([f"python3 {file_path} -c {syncfile}"], shell=True)    
            time.sleep(interval_minutes*60)
        except:
            break

# Run synchronization process
p_sync = multiprocessing.Process(target=regular_time_sync, args=(), daemon=True)
p_sync.start()

# TCP control socket
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.connect((HOST, 3299))


# Create DL receive and UL transmit multi-client sockets
rx_sockets = []
tx_sockets = []
for dev, port in zip(devices, ports):
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, (dev+'\0').encode())
    rx_sockets.append(s1)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, (dev+'\0').encode())
    tx_sockets.append(s2)
    print(f'Create DL socket for {dev}.')
    print(f'Create UL socket for {dev}.')
    
# Transmit data from receive socket to server DL port to let server know addr first
while True:
    give_server_DL_addr()
    break
print('Finished giving server DL socket address!')

pcap_path = '/home/wmnlab/temp'
tcpproc_list = []
for device, port in zip(devices, ports):
    pcap = os.path.join(pcap_path, f"client_pcap_BL_{device}_{port[0]}_{port[1]}_{n}_sock.pcap")
    tcpproc = subprocess.Popen([f"tcpdump -i any port '({port[0]} or {port[1]})' -w {pcap}"], shell=True, preexec_fn=os.setpgrp)
    tcpproc_list.append(tcpproc)
time.sleep(1)

# Create and start DL receive multi-thread
rx_threads = []
for s, dev in zip(rx_sockets, devices):
    t_rx = threading.Thread(target=receive, args=(s, dev, ), daemon=True)
    rx_threads.append(t_rx)
    t_rx.start()

# Create and start UL transmission multiprocess
p_tx = multiprocessing.Process(target=transmit, args=(tx_sockets,), daemon=True)
p_tx.start()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)

# Main Process waiing...
try:

    indata = s_tcp.recv(1024)
    print('received ' + indata.decode() + ' command from server')

    stop_threads = True

    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin process
    p_sync.terminate()
    print("regular time sync process closed")

    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

    exit(0)

except SystemExit as e: print('Successfully closed.')
except BaseException as e:

    print(e)

    outdata = 'CLOSE'
    s_tcp.send(outdata.encode())
    stop_threads = True

    # Kill tcp control
    s_tcp.close()
    print('TCP control closed')

    # Kill transmit process
    p_tx.terminate()
    p_tx.join()
    print('p_tx trminated')

    # Kill time synchronizatoin process
    p_sync.terminate()
    print("regular time sync process closed")

    for tcpproc in tcpproc_list:
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)

    print('Error, closed.')
