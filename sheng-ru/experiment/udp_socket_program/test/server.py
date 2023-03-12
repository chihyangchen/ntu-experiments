#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import threading
import os
import datetime as dt
import argparse
import subprocess
from device_to_port import device_to_port, port_to_device


#=================argument parsing======================
parser = argparse.ArgumentParser()
# parser.add_argument("-ps", "--port_start", type=int,
#                     help="port to bind, range: [start, end]", default=3280)
# parser.add_argument("-pe", "--port_end", type=int,
#                     help="port to bind, range: [start, end]", default=3287)
# parser.add_argument("-l", "--length", type=int,
#                     help="payload length", default=250)
# parser.add_argument("-b", "--bandwidth", type=int,
#                     help="data rate (bits per second)", default=200000)   
# parser.add_argument("-t", "--time", type=int,
#                     help="maximum experiment time", default=3600)
parser.add_argument("-n", "--number_client", type=int,
                    help="number of client", default=1)
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
        ports.append((device_to_port[device][0]))  # default uplink port for each device
        ports.append((device_to_port[device][1]))  # default downlink port for each device
else:
    for port in args.ports:
        if '-' in port:
            start = int(port[:port.find('-')])
            stop = int(port[port.find('-') + 1:]) + 1
            for i in range(start, stop):
                ports.append(i)
            continue
        ports.append(int(port))

if True:
    PORTS = ports[::2]
else:
    PORTS = ports[1::2]

print(devices)
print(PORTS)

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
# number_client = len(args.devices)
# number_client = 1

expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
#========================================================

#=================global variables=======================
thread_stop = True
exit_main_process = False
udp_addr = {}
#========================================================

#=================other variables========================
HOST = '0.0.0.0'
CONTROL_PORT = 3299

def makedir(dirpath, mode=0):  # mode=1: show message, mode=0: hide message
    if os.path.isdir(dirpath):
        if mode:
            print("mkdir: cannot create directory '{}': directory has already existed.".format(dirpath))
        return
    ### recursively make directory
    _temp = []
    while not os.path.isdir(dirpath):
        _temp.append(dirpath)
        dirpath = os.path.dirname(dirpath)
    while _temp:
        dirpath = _temp.pop()
        print("mkdir", dirpath)
        os.mkdir(dirpath)

now = dt.datetime.today()
date = [str(x) for x in [now.year, now.month, now.day]]
date = [x.zfill(2) for x in date]
date = '-'.join(date)
makedir("./log/{}".format(date))

pcap_path = "./log/{}/{}".format(date, "server_pcap")  # wireshark capture
makedir(pcap_path)
ss_path = "./log/{}/{}".format(date, "server_ss")      # socket statistics (Linux: ss)
makedir(ss_path)
#========================================================

def connection_setup():
    print("Initial setting up...")
    
    s_udp_list = []
    s_udp_ul_list = []
    s_udp_dl_list = []
    conn_list = []
    
    #--------------establish sockets for UDP data traffic----- 
    for PORT in PORTS:
        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_udp.bind((HOST, PORT))
        s_udp_list.append(s_udp)
    
    # for PORT in UL_PORTS:
    #     s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s_udp.bind((HOST, PORT))
    #     s_udp_ul_list.append(s_udp)
    # for PORT in DL_PORTS:
    #     s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s_udp.bind((HOST, PORT))
    #     s_udp_dl_list.append(s_udp)
    
    #--------------establish TCP control flows----------------
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
    s_tcp.bind((HOST, CONTROL_PORT))

    # print(PORTS, "wait for tcp connection...")
    print((HOST, CONTROL_PORT), "wait for tcp control connection...")
    s_tcp.listen(number_client)

    for port in zip(PORTS):
        print((HOST, port), "wait for udp connection...")
    
    for i in range(number_client):
        conn, tcp_addr = s_tcp.accept()
        print('tcp Connected by', tcp_addr)
        conn_list.append(conn)
    
    # print((HOST, CONTROL_PORT), "wait for connection...")
    # s_tcp.listen(1)
    # conn, tcp_addr = s_tcp.accept()
    # print('tcp Connected by', tcp_addr)
    # print((host, port), "connection setup complete")
    # result[0] = s_tcp, conn, tcp_addr

    return s_tcp, s_udp_list, conn_list
    # return s_tcp, s_udp_ul_list, s_udp_dl_list, conn_list

def transmission(s_udp_list):
    global thread_stop
    global udp_addr
    print("start transmission: ")
    
    seq = 1
    prev_transmit = 0
    
    start_time = time.time()
    next_transmit_time = start_time + sleeptime
    
    time_slot = 1
    
    while time.time() - start_time < total_time and not thread_stop:
    
        t = time.time()
        while t < next_transmit_time:
            t = time.time()
        next_transmit_time = next_transmit_time + sleeptime
        
        euler = 271828
        pi = 31415926
        datetimedec = int(t)
        microsec = int((t - int(t))*1000000)
        
        # redundant = os.urandom(length_packet-4*3)
        # outdata = datetimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant

        redundant = os.urandom(length_packet-4*5)
        outdata = euler.to_bytes(4, 'big') + pi.to_bytes(4, 'big') + datetimedec.to_bytes(4, 'big') + microsec.to_bytes(4, 'big') + seq.to_bytes(4, 'big') + redundant
        
        for s_udp in s_udp_list:
            if s_udp in udp_addr.keys():
                s_udp.sendto(outdata, udp_addr[s_udp])
        seq += 1
        
        if time.time()-start_time > time_slot:
            print("[%d-%d]"%(time_slot-1, time_slot), "transmit", seq-prev_transmit)
            time_slot += 1
            prev_transmit = seq
            
    
    print("---transmission timeout---")
    print("transmit", seq, "packets")


def receive(s_udp):
    s_udp.settimeout(5)
    print("wait for indata...")
    number_of_received_packets = 0
    
    seq = 1
    max_seq = 1

    global thread_stop
    global udp_addr
    while not thread_stop:
        try:
            #receive data, update client's addresses (after receiving, server know where to transmit)
            indata, addr = s_udp.recvfrom(1024)
            udp_addr[s_udp] = addr                     
            
            if len(indata) != length_packet:
                print("packet with strange length: ", len(indata))
            # seq = int(indata.hex()[16:24], 16)
            seq = int(indata.hex()[32:40], 16)
            max_seq = max(max_seq, seq)
            
            # ts = int(int(indata.hex()[0:8], 16)) + float("0." + str(int(indata.hex()[8:16], 16)))
            ts = int(int(indata.hex()[16:24], 16)) + float("0." + str(int(indata.hex()[24:32], 16)))
            
            number_of_received_packets += 1
            
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    
    print("---Experiment Complete---")
    print("Total capture: ", number_of_received_packets, "Total loss: ", max_seq - number_of_received_packets)
    print("STOP bypass")

os.system("echo wmnlab | sudo -S su")
while not exit_main_process:
    # if not os.path.exists(pcap_path):
    #     os.system("mkdir %s"%(pcap_path))

    now = dt.datetime.today()
    # n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    n = [str(x) for x in [now.year, now.month, now.day, now.hour, now.minute, now.second]]
    n = [x.zfill(2) for x in n]  # zero-padding to two digit
    n = '-'.join(n[:3]) + '_' + '-'.join(n[3:])
    
    #Create subprocesses to capture packets (TCPDUMP)
    tcpproc_list = []
    # tcpproc =  subprocess.Popen(["sudo tcpdump -i any port 3299 -w %s/3299_%s.pcap"%(pcap_path,n)], shell=True, preexec_fn = os.setpgrp)
    # tcpproc_list.append(tcpproc)
    for device, PORT in zip(devices, PORTS):
        pcap = os.path.join(pcap_path, "server_pcap_BL_{}_{}_{}_sock.pcap".format(device, PORT, n))
        tcpproc =  subprocess.Popen(["sudo tcpdump -i any port {} -w {}".format(PORT, pcap)], shell=True, preexec_fn = os.setpgrp)
        tcpproc_list.append(tcpproc)
        
    time.sleep(1)
    
    receiving_threads = []
    udp_addr = {}

    try:
        s_tcp, s_udp_list, conn_list = connection_setup()
        # s_tcp, s_udp_ul_list, s_udp_dl_list, conn_list = connection_setup()
        
        while thread_stop == True:
            control_message = input("Enter START to start: ")
            if control_message == "START":
                thread_stop = False
                
                for conn in conn_list:
                    conn.sendall("START".encode())
                t = threading.Thread(target = transmission, args = (s_udp_list, ))
                # t = threading.Thread(target = transmission, args = (s_udp_dl_list, ))
                t.start()
                print("*************hello1****************")
                for s_udp in s_udp_list:
                # for s_udp in s_udp_ul_list:
                    t1 = threading.Thread(target = receive, args = (s_udp,))
                    t1.start()
                    receiving_threads.append(t1)
        print("******************hello2****************")
        
    except KeyboardInterrupt as inst:
        print("keyboard interrupt: ")
        #Kill TCPDUMP subprocesses
        for tcpproc in tcpproc_list:
            pgid = os.getpgid(tcpproc.pid)
    
            command = "sudo kill -9 -{}".format(pgid)
            subprocess.check_output(command.split(" "))
        exit()
    except Exception as e:
        print("Connection Error:", e)
        exit()
    

    try:
        while t.is_alive():
            print("*****************hello3*****************")
            control_message = input("Enter STOP to stop: ")
            if control_message == "STOP":
                thread_stop = True
                for conn in conn_list:
                    conn.sendall("STOP".encode())
                break
            elif control_message == "EXIT":
                thread_stop = True
                exit_main_process = True
                for conn in conn_list:
                    conn.sendall("EXIT".encode())
                break    
    except Exception as e:
        print(e)
        exit_main_progress = True
    finally:
        print("finally")
        
        thread_stop = True
        
        #end transmission and receive threads
        t.join()
        for t1 in receiving_threads:
            t1.join()
        
        #close sockets
        s_tcp.close()
        for s_udp in s_udp_list:
            s_udp.close()
        # for s_udp in s_udp_ul_list:
        #     s_udp.close()
        # for s_udp in s_udp_dl_list:
        #     s_udp.close()
            
        #Kill TCPDUMP subprocesses
        for tcpproc in tcpproc_list:
            pgid = os.getpgid(tcpproc.pid)
    
            command = "sudo kill -9 -{}".format(pgid)
            subprocess.check_output(command.split(" "))
