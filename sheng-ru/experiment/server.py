#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import argparse
import sys
import time
import signal
import subprocess
import os
import threading
import multiprocessing

# Default parameter
HOST = '0.0.0.0' # 140.112.20.183
PORT = 3250
pcap_path = '/home/wmnlab/D/sheng-ru/ntu-experiments/sheng-ru/experiment/123.pcap'

#====================argument parsing==============================
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=PORT)
parser.add_argument("-l", "--length", type=int,
                    help="payload length", default=250)
parser.add_argument("-b", "--bandwidth", type=int,
                    help="data rate (bits per second)", default=200000)   
parser.add_argument("-t", "--time", type=int,
                    help="maximum experiment time", default=3600)

args = parser.parse_args()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, args.port))

length_packet = args.length
bandwidth = args.bandwidth
total_time = args.time

expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec

#==================================================================
print('server start at: %s:%s' % (HOST, args.port))
print('wait for connection...')
tcpdumpproc = subprocess.Popen([f"tcpdump -i any port {args.port} -w {pcap_path}"],
            shell=True, start_new_session=True)

# Transmit function define
seq = 1
prev_transmit = 1

start_time = time.time()
next_transmit_time = start_time + sleeptime

udp_addrs = {}

def transmit():
    
    global start_time, seq, prev_transmit, next_transmit_time, udp_addrs
    time_slot = 1

    while time.time() - start_time < total_time:

        t = time.time()
        while t < next_transmit_time:
            t = time.time()
        next_transmit_time = next_transmit_time + sleeptime

        datetimedec = int(t)
        microsec = int((t - int(t))*1000000)

        redundant = os.urandom(length_packet-4*3)
        outdata = datetimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant
        
        for i in udp_addrs:
            s.sendto(outdata, udp_addrs[i]) ## ?????
            print('yes')

        seq += 1

        if time.time() - start_time > time_slot:
            print("[%d-%d]"%(time_slot-1, time_slot), "transmit", seq-prev_transmit, f'| seq: {seq}')
            time_slot += 1
            prev_transmit = seq
            print(udp_addrs)

# Receive function define

def receive():
    
    global udp_addrs
    time_slot = 1
    max_seq = 1
    prev_recv = 1
    
    while True:
        
        try:
            indata, addr = s.recvfrom(1024)
            udp_addrs[0] = addr

            try: start_recieve_time
            except NameError: 
                start_recieve_time = time.time()
            if len(indata) != length_packet:
                print("packet with strange length: ", len(indata))

            rec_seq = int(indata.hex()[16:24], 16)
            max_seq = max(max_seq, rec_seq)
            ts = int(int(indata.hex()[0:8], 16)) + float("0." + str(int(indata.hex()[8:16], 16)))

            if time.time()-start_recieve_time > time_slot:
                print("[%d-%d]"%(time_slot-1, time_slot), "recieve", rec_seq-prev_recv, f'| seq: {rec_seq}')
                time_slot += 1
                prev_recv = rec_seq
                print(udp_addrs)

        except Exception:
            print('STOP')
        
# Receive process
p1 = multiprocessing.Process(target = receive)
p1.start()

# Transmit process
p2 = multiprocessing.Process(target = transmit)
p2.start()

try:
    while 1:
        time.sleep(.1)
except KeyboardInterrupt:
    p2.terminate()
    print("Terminate transmit process.")
    p1.terminate()
    print("Terminate receive process.")
    os.killpg(os.getpgid(tcpdumpproc.pid), signal.SIGTERM)
    print("Kill tcpdump process.")
    s.close()

# while True:
#     try:
#         # Receive
#         indata, addr = s.recvfrom(1024)
#         print(addr)

#         try: start_time
#         except NameError: 
#             start_time = time.time()

#         if len(indata) != length_packet:
#             print("packet with strange length: ", len(indata))

#         seq = int(indata.hex()[16:24], 16)
#         max_seq = max(max_seq, seq)
#         ts = int(int(indata.hex()[0:8], 16)) + float("0." + str(int(indata.hex()[8:16], 16)))

#         if time.time()-start_time > time_slot:
#             print("[%d-%d]"%(time_slot-1, time_slot), "recieve", seq-prev_transmit, f'| seq: {seq}')
#             time_slot += 1
            
#             prev_transmit = seq
    
#     except KeyboardInterrupt:
#         os.killpg(os.getpgid(p.pid), signal.SIGTERM)
#         s.close()
#         sys.exit()

#     except:
#         pass



# def transmit(total_time):

#     start_time = time.time()
#     next_transmit_time = start_time + sleeptime

#     while time.time() - start_time < total_time:

#         try:
#             # Transmit
#             t = time.time()
#             while t < next_transmit_time:
#                 t = time.time()
#             next_transmit_time = start_time + sleeptime

#             datetimedec = int(t)
#             microsec = int((t-int(t))*1000000)

#             redundant = os.urandom(length_packet-4*3)
#             outdata = datatimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant

#             s.sendto(outdata, udp_addr[1])