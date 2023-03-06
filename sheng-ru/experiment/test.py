import os
import subprocess
import threading

subprocess.Popen(['sudo tcpdump port 3250 -w /home/wmnlab/123.pcap'],  shell=True, preexec_fn = os.setpgrp)
os.system('iperf3 -s -B 0.0.0.0 -p 3250')
