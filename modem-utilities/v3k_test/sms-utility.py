#!/usr/bin/python3
#python3 sms-utility.py SENDING_INTERFACE PHONE ERROR_CASE(1-5;0 for normal)

import os
import sys

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

print(MESSAGE)


#os.system('sms-send.sh -i ' + SENDING_INTERFACE + ' -n ' + PHONE + ' -m ' + MESSAGE)
