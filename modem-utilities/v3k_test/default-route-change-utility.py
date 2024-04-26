#!/usr/bin/python3

# python3 FROM_INTERFACE test eth_INTERFACE eth_GW
#
#

import sys
import os
import subprocess,shlex

BASH_PATH="/home/moxa/young/ntu-experiments/modem-utilities/v3k_test"
V3K_USE='/v3k_test/'

FROM_INTERFACE = sys.argv[1]
TO_INTERFACE = ""
result=""
with open('/usr/local/bin/PATH_for_NTU_exp','r') as p:
	re=p.readlines()
for line in re:
	line = line.split('=')
	if line[0] == 'PATH_UTILS':
		BASH_PATH = line[1][1:-2] + V3K_USE

if len(sys.argv) < 3:
	if FROM_INTERFACE[-1] == "1":
		TO_INTERFACE = FROM_INTERFACE[:-1] + "2"
	else:
		TO_INTERFACE = FROM_INTERFACE[:-1] + "1"
#	os.system(BASH_PATH + 'default-route-change.sh -f ' + FROM_INTERFACE + ' -t ' + TO_INTERFACE)
	cmd = BASH_PATH + 'default-route-change.sh -f ' + FROM_INTERFACE + ' -t ' + TO_INTERFACE
	result=subprocess.run(shlex.split(cmd))
	exit(result.returncode)
else:
	if sys.argv[2] == "test":
		TO_INTERFACE = sys.argv[3]
		eth_GW = sys.argv[4]
		if len(sys.argv) > 5 and sys.argv[5] == "B":
			os.system(BASH_PATH + 'default-route-change.sh -f ' + TO_INTERFACE + ' -t ' + FROM_INTERFACE + ' -T -G ' + eth_GW)
		else:
			os.system(BASH_PATH + 'default-route-change.sh -f ' + FROM_INTERFACE + ' -t ' + TO_INTERFACE + ' -T -G ' + eth_GW)



