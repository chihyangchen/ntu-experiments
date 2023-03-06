import subprocess
import time
import datetime as dt
import os
import signal

port1 = 3250
port2 = 3251

now = dt.datetime.today()
t = '-'.join([str(x) for x in[ now.year%100, now.month, now.day, now.hour, now.minute]])
# save file to 
save_file = f"/home/wmnlab/D/sheng-ru/Data/{t}_server.pcap"
tcpproc = subprocess.Popen([f"tcpdump -i any port {port1} or port {port2} -w {save_file}"],
                            shell=True, preexec_fn=os.setsid)
time.sleep(1)

iperfproc1 = subprocess.Popen([f"iperf3 -s -B 0.0.0.0 -p {port1}"], shell=True, preexec_fn=os.setsid)
iperfproc2 = subprocess.Popen([f"iperf3 -s -B 0.0.0.0 -p {port2}"], shell=True, preexec_fn=os.setsid)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)
    os.killpg(os.getpgid(iperfproc1.pid), signal.SIGTERM)
    os.killpg(os.getpgid(iperfproc2.pid), signal.SIGTERM)