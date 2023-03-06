#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import argparse
import time
import os

HOST = '140.112.20.183'
PORT = 3250
#   ========================================================
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--host", type=str,
                    help="server ip", default=HOST)
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=PORT)
parser.add_argument("-l", "--length", type=int,
                    help="payload length", default=250)
parser.add_argument("-b", "--bandwidth", type=int,
                    help="data rate (bits per second)", default=200000)   
parser.add_argument("-t", "--time", type=int,
                    help="maximum experiment time", default=3600)  

args = parser.parse_args()

server_addr = (args.host, args.port)
length_packet = args.length
bandwidth = args.bandwidth
total_time = args.time

expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')

seq = 1
prev_transmit = 0
time_slot = 1

start_time = time.time()
next_transmit_time = start_time + sleeptime

while time.time() - start_time < total_time:
    t = time.time()
    while t < next_transmit_time:
        t = time.time()
    next_transmit_time = next_transmit_time + sleeptime

    datetimedec = int(t)
    microsec = int((t - int(t))*1000000)

    redundant = os.urandom(length_packet-4*3)
    outdata = datetimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant

    s.sendto(outdata, (args.host, args.port))
    seq += 1

    # Show information
    if time.time()-start_time > time_slot:
        print("[%d-%d]"%(time_slot-1, time_slot), "transmit", seq-prev_transmit)
        time_slot += 1
        prev_transmit = seq

s.close()