#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import socket
import time
import json
import datetime as dt

def mean(numbers):
    if len(numbers) == 0:
        return 0
    _sum = 0
    for item in numbers:
        _sum += item
    return _sum / len(numbers)

def quantile(data, q):
    q /= 100
    sorted_data = sorted(data)
    n = len(sorted_data)
    index = q * (n - 1)
    if index.is_integer():
        return sorted_data[int(index)]
    else:
        lower = sorted_data[int(index)]
        upper = sorted_data[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))

def qset_bdd(client_rtt):
    # Look for the range of the outliers.
    sorted_rtt = sorted([s[3] for s in client_rtt])
    
    upper_q = quantile(sorted_rtt, 75)
    lower_q = quantile(sorted_rtt, 25)
    iqr = (upper_q - lower_q) * 1.5
    
    qset = (lower_q - iqr, upper_q + iqr)
    return qset

def clock_diff(timestamp_server, timestamp_client):
    client = [[*s, float(s[2]) - float(s[1])] for s in timestamp_client]
    server = timestamp_server[:]
    
    diff = 0.0
    qset = qset_bdd(client)
    deltas = []
    for i in range(len(client)):
        RTT = client[i][3]
        if (RTT < qset[0]) or (RTT > qset[1]):
            continue
        cen_client = (float(client[i][2]) + float(client[i][1]))/2
        cen_server = (float(server[i][2]) + float(server[i][1]))/2
        diff = cen_server - cen_client
        deltas.append(diff)
    
    sorted_deltas = sorted(deltas)
    upper_q = quantile(sorted_deltas, 75)
    lower_q = quantile(sorted_deltas, 25)
    iqr = (upper_q - lower_q) * 1.5
    qset = (lower_q - iqr, upper_q + iqr)
    
    deltas = [s for s in deltas if s >= qset[0] and s <= qset[1]]
    diff = mean(deltas)

    # diff > 0: client is behind server by abs(diff) seconds
    # diff < 0: client is ahead of server by abs(diff) seconds
    return diff

HOST = '140.112.20.183'
PORT = 3298

# client
if sys.argv[1] == '-c':
    
    file_path = sys.argv[2]
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    print('Synchronizing...')
    
    server_addr = (HOST, PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    num_packet_per_round = 200
    packet_interval = 0

    timestamp_client = []
    timestamp_server = []

    i = 0
    ctmo_cnt = 0
    while i <= num_packet_per_round:
        time0 = time.time()
        outdata = str(i).zfill(3)
        s.sendto(outdata.encode(), server_addr)
        s.settimeout(3)
        try:
            indata, addr = s.recvfrom(1024)
            time1 = time.time()
            indata = indata.decode()
            ctmo_cnt = 0
        except:
            # print("tiem sync packet timeout", outdata)
            ctmo_cnt += 1
            if ctmo_cnt == 3:
                print("Too many time sync packet timeout")
                break
            continue
        timestamp_client.append([outdata, time0, time1])
        timestamp_server.append(indata.split(' '))
        time.sleep(packet_interval)
        i += 1
    outdata = 'end'
    s.sendto(outdata.encode(), server_addr)
    
    current_time = dt.datetime.now()
    diff = clock_diff(timestamp_server, timestamp_client)
    print(f'Time: {current_time};', f'Clock Diff: {diff}', "seconds")
    
    file_path = os.path.join(dir_path, file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            json_object = json.load(f)
    else:
        json_object = {}
    json_object[str(current_time)] = diff
    with open(file_path, 'w') as f:
        json.dump(json_object, f)

# server
elif sys.argv[1] == '-s':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', PORT))

    try: 
        while True:
            print('server start at: %s:%s' % ('0.0.0.0', PORT))
            print('wait for connection...')

            while True:
                indata, addr = s.recvfrom(1024)
                time0 = time.time()
                indata = indata.decode()
                if indata == 'end':
                    break
                
                time1 = time.time()
                outdata = f'{indata} {time0} {time1}'
                s.sendto(outdata.encode(), addr)
            print('finished synchronization!')
    except BaseException as e:
        print(e)
        print('close synchronization socket')