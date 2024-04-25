#!/usr/bin/python3
#python3 sms-utility.py SENDING_INTERFACE PHONE ERROR_CASE(1-5;0 for normal)

import os
import sys
import subprocess,shlex


SENDING_INTERFACE=sys.argv[1]
PHONE=sys.argv[2]

if SENDING_INTERFACE == "m11" or SENDING_INTERFACE == "m12":
	DEV = "Metro#1"
elif SENDING_INTERFACE == "m21" or SENDING_INTERFACE == "m22":
	DEV = "Metro#2"
elif SENDING_INTERFACE == "m31" or SENDING_INTERFACE == "m32":
	DEV = "Metro#3"
elif SENDING_INTERFACE == "m41" or SENDING_INTERFACE == "m42":
	DEV = "Metro#4"
if SENDING_INTERFACE[-1] == "1":
	ERROR_INTERFACE = SENDING_INTERFACE[:-1] + "2"
elif SENDING_INTERFACE[-1] == "2":
	ERROR_INTERFACE = SENDING_INTERFACE[:-1] + "1"

if sys.argv[3] == "1":
	MESSAGE="Lost-Connection"
elif sys.argv[3] == "2":
	MESSAGE="Flight-Mode-Toggling"
elif sys.argv[3] == "3":
	MESSAGE="Pwr-GPIO-Toggling"
elif sys.argv[3] == "4":
	MESSAGE="SIM-Error"
elif sys.argv[3] == "5":
	MESSAGE="Thermal-Alarm"
	ERROR_INTERFACE = "SYSTEM"	
else:
	MESSAGE="Normal-Sending"
	ERROR_INTERFACE = SENDING_INTERFACE	
MESSAGE =  DEV + "-" + ERROR_INTERFACE + ":" + MESSAGE

BASH_PATH="/home/moxa/young/ntu-experiments/modem-utilities/v3k_test"
V3K_USE='/v3k_test/'

with open('/usr/local/bin/PATH_for_NTU_exp','r') as p:
    re=p.readlines()
for line in re:
    line = line.split('=')
    if line[0] == 'PATH_UTILS':
        BASH_PATH = line[1][1:-2] + V3K_USE
print(MESSAGE)
cmd = BASH_PATH + 'sms-send.sh -i ' + SENDING_INTERFACE + ' -n ' + PHONE + ' -m ' + MESSAGE
result=subprocess.run(shlex.split(cmd))
exit(result.returncode)

#os.system(BASH_PATH + 'sms-send.sh -i ' + SENDING_INTERFACE + ' -n ' + PHONE + ' -m ' + MESSAGE)
