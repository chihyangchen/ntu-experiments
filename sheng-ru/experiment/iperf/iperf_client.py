import subprocess
import time
import datetime as dt
import os
import signal

server_ip = '140.112.20.183'
port1 = 3350
port2 = 3351
packet_length = 500 # bytes
band_width = '200K' # bits/sec
experiment_time = 3600 # sec

now = dt.datetime.today()
t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
save_file = f"/sdcard/dataset/{t}_client.pcap"
tcpproc = subprocess.Popen([f"tcpdump -i any port {port1} or port {port2} -w {save_file}"],
                            shell=True, preexec_fn=os.setsid)

time.sleep(1)
# UL
iperfproc1 = subprocess.Popen([f"iperf3 -c {server_ip} -p {port1} -b {band_width} -l {packet_length} -t {experiment_time}"], 
                             shell=True, preexec_fn=os.setsid)
# -R: server sends, client receive -> DL
iperfproc2 = subprocess.Popen([f"iperf3 -c {server_ip} -p {port2} -b {band_width} -l {packet_length} -t {experiment_time} -R"], 
                             shell=True, preexec_fn=os.setsid)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)
    os.killpg(os.getpgid(iperfproc1.pid), signal.SIGTERM)
    os.killpg(os.getpgid(iperfproc2.pid), signal.SIGTERM)