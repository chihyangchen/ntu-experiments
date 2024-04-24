#!/usr/bin/python3

# python3 FROM_INTERFACE test eth_INTERFACE eth_GW
#
#

import sys
import os

BASH_PATH="/home/moxa/young/ntu-experiments/modem-utilities/v3k_test"

FROM_INTERFACE = sys.argv[1]
TO_INTERFACE = ""

if len(sys.argv) < 2:
	if FROM_INTERFACE[-1] == "1":
		TO_INTERFACE = FROM_INTERFACE[:-1] + "2"
	else:
		TO_INTERFACE = FROM_INTERFACE[:-1] + "1"
else:
	if sys.argv[2] == "test":
		TO_INTERFACE = sys.argv[3]
		eth_GW = sys.argv[4]
		if len(sys.argv) > 5 and sys.argv[5] == "B":
			os.system(BASH_PATH + '/default-route-change-test.sh -f ' + TO_INTERFACE + ' -t ' + FROM_INTERFACE + ' -T -G ' + eth_GW)
		else:
			os.system(BASH_PATH + '/default-route-change-test.sh -f ' + FROM_INTERFACE + ' -t ' + TO_INTERFACE + ' -T -G ' + eth_GW)

		

#print("FROM:",FROM_INTERFACE)
#print("TO:",TO_INTERFACE)
#print("eth_GW",eth_GW)

