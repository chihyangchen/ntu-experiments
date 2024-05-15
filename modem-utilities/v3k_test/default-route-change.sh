#!/bin/bash
####
# Under development
# Switch the default route in NTU experiment
###
source PATH_for_NTU_exp
SUDO=sudo
ETH_GW="172.30.30.25"
#ETH_GW=""

function PING_DEV() {
	ping 8.8.8.8 -c 1 -W 2 -I $1
}

INTERVAL_PING=2	# interval of ping (second)
MAX_FAIL=5	# max. failed count; default route will be switched when reach this value
TEST=""
helpFunction()
{
	echo ""
	echo "Usage: $0 -f [FROM INTERFACE] -t [TO_INTERFACE] [-T for test]"
	echo "INTERFACE: INTERFACE name eg. wwan0"
	exit 1 # Exit script after printing help
}

while getopts "f:t:G:T" opt
do
	case "$opt" in
		f ) FROM_INTERFACE="$OPTARG" ;;
		t ) TO_INTERFACE="$OPTARG" ;;
		T ) TEST="test" ;;
		G ) ETH_GW="$OPTARG" ;;
		? ) helpFunction ;;
	esac
done

if [ -z "$FROM_INTERFACE" ] ||  [ -z "$TO_INTERFACE" ]
then
	echo "missing argument"
	helpFunction
fi

FROM_GW=""
TO_GW=""
COUNT_FAIL=0
DNS_PRIMARY=""
DNS_SECONDARY=""

function UPDATE_GW() {

	path="$PATH_TEMP_DIR/temp"
	wds_ip_filter="$path/temp-ip-setting_$1"
	if [ -f $wds_ip_filter ];
	then
		if [ "$1" == "$TO_INTERFACE" ]
		then
			TO_GW=`(cat $wds_ip_filter | head -3 | tail -1)`
		elif [ "$1" == "$FROM_INTERFACE" ]
		then
			FROM_GW=`(cat $wds_ip_filter | head -3 | tail -1)`
		fi
	#fi
	### IF use two module, comment the belowing code
	elif [ "$TEST" == "test" ]
	then	
		if [ "$1" == "$TO_INTERFACE" ]
		then
			TO_GW=$ETH_GW
			echo "$TO_GW"	
		elif [ "$1" == "$FROM_INTERFACE" ]
		then
			FROM_GW=$ETH_GW
			echo "$FROM_GW"	
		fi
	###  Above ######################################
		
	fi
}
function ROUTE_CHANGE() {   # 1 -> 2
	echo -n "[ROUTE_CHANGE]: "
	LC_GW_FROM=$FROM_GW
	LC_GW_TO=$TO_GW

	if  [[ $(ip route | grep default | head -1 | grep $TO_INTERFACE) ]]
	then
		echo "TARGET is the FIRST Default, No need to CHANGE"
		return 0
	elif ! [[ $(ip route | grep default | grep $TO_INTERFACE) ]]
	then		
		${SUDO} ip route append default via $LC_GW_TO
		sleep 0.1
	fi
	${SUDO} ip route del default dev $FROM_INTERFACE
	sleep 0.1
	${SUDO} ip route append default via $LC_GW_FROM	# add to the last
	echo " From $FROM_INTERFACE to $TO_INTERFACE"	
}

function DNS_CHANGE() {
	path="$PATH_TEMP_DIR/temp"
	wds_ip_filter="$path/temp-ip-setting_$1"
	if [ -f $wds_ip_filter ];
	then
		DNS_PRIMARY=`(cat $wds_ip_filter | tail -3 | head -2 | head -1)`
		DNS_SECONDARY=`(cat $wds_ip_filter | tail -3 | head -2 | tail -1)`
	fi
	echo "nameserver $DNS_PRIMARY" | ${SUDO} tee /etc/resolv.conf > /dev/null 2>&1
	echo "nameserver $DNS_SECONDARY" | ${SUDO} tee -a /etc/resolv.conf > /dev/null 2>&1
}



# update the current gateways
UPDATE_GW $TO_INTERFACE
UPDATE_GW $FROM_INTERFACE

	####Check if default route exist####
while ! [[ $(ip route | grep default) ]] && [ $COUNT_FAIL -lt $MAX_FAIL ]
do
	echo "no any default route exists"
	sleep 1
	if [[ $(ip route | grep $TO_INTERFACE) ]]
	then
		UPDATE_GW $TO_INTERFACE
		DNS_CHANGE $TO_INTERFACE
		${SUDO} ip route append default via $TO_GW
	fi
	let COUNT_FAIL+=1
	echo "COUNT FAIL: $COUNT_FAIL, MAX_FAIL: $MAX_FAIL"
done
if ! [ $COUNT_FAIL -lt $MAX_FAIL ]
then
	echo "REACH the MAX FAIL"
	exit 1
fi

	####Check if the other interface is working####
COUNT_FAIL=0
PING_DEV $TO_INTERFACE > /dev/null 2>&1
result=$?

while [ $result != 0 ] && [ $COUNT_FAIL -lt $MAX_FAIL ]
do
	sleep $INTERVAL_PING	# interval of ping (second)
	let COUNT_FAIL+=1
	PING_DEV $TO_INTERFACE > /dev/null 2>&1
	result=$?
	echo "COUNT FAIL: $COUNT_FAIL, MAX_FAIL: $MAX_FAIL"
done

if [ $result != 0 ]
then
	echo "TARGET INTERFACE is FAILED"
	#### DO OTHER PROCESS
	exit 1
else
	### CHANGE THE DEFAULT
	echo "TARGET INTERFACE is WORKED, READY TO CHANGE"

	# update GW
	UPDATE_GW $FROM_INTERFACE
	UPDATE_GW $TO_INTERFACE
	# change default
	ROUTE_CHANGE 
	# update DNS
	DNS_CHANGE $TO_INTERFACE
fi


