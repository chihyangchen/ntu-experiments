#!/bin/bash
####
# Under development
# Still need to manual add the gateway IP and Interface name
###
source PATH_for_NTU_exp
SUDO=sudo

function PING_DEV() {
	ping 8.8.8.8 -c 1 -W 1 -I $1
}

INTERVAL_PING=5	# interval of ping (second)
MAX_FAIL=5	# max. failed count; default route will be switched when reach this value

INTERFACE_1="enp16s0"
INTERFACE_2="m21"


GW_1="172.30.30.254"
GW_2="ssss"
COUNT_FAIL_1=0
COUNT_FAIL_2=0

function UPDATE_GW() {

	path="$PATH_TEMP_DIR/temp"
	wds_ip_filter="$path/temp-ip-setting_$1"
	if [ -f $wds_ip_filter ];
	then
		if [ "$1" == "$INTERFACE_1" ]
		then
			GW_1=`(cat $wds_ip_filter | tail -2 | head -1)`
		elif [ "$1" == "$INTERFACE_2" ]
		then
			GW_2=`(cat $wds_ip_filter | tail -2 | head -1)`
		fi
	fi
}

function ROUTE_CHANGE() {   # 1 -> 2
    LC_GW_FROM=""
	LC_GW_TO=""
	if [ "$1" == "$INTERFACE_1" ]
	then
		LC_GW_FROM=$GW_1
		LC_GW_TO=$GW_2
	elif [ "$1" == "$INTERFACE_2" ]
	then
		LC_GW_FROM=$GW_2
		LC_GW_TO=$GW_1
	fi


    if ! [[ $(ip route | grep default | grep $2) ]]
	then		
       ${SUDO} ip route append default via $LC_GW_TO
    fi
    ${SUDO} ip route del default dev $1
    ${SUDO} ip route append default via $LC_GW_FROM	# add to the last
}





# temporary use
UPDATE_GW $INTERFACE_2
echo "$GW_2"

while true
do
	PING_DEV $INTERFACE_1 > /dev/null 2>&1
	if [ $? != 0 ]
	then
		let COUNT_FAIL_1+=1
#		echo " FAIL 1: $COUNT_FAIL_1"
	else
		COUNT_FAIL_1=0
	fi
	

    PING_DEV $INTERFACE_2 > /dev/null 2>&1
    if [ $? != 0 ]
    then
        let COUNT_FAIL_2+=1
#		UPDATE_GW $INTERFACE_2
#        echo " FAIL 2: $COUNT_FAIL_2"
    else
        COUNT_FAIL_2=0
    fi

	while ! [[ $(ip route | grep default) ]]
	do
		echo "no any default route exists"
		sleep 1
	done 
	# check the current defaut route and if it works
	if [[ $(ip route | head -1 | grep default | grep $INTERFACE_1) ]] && [ $COUNT_FAIL_1 == 0 ];
	then
		echo "$INTERFACE_1 is in default and is working"

	elif [[ $(ip route | head -1 | grep default | grep $INTERFACE_2) ]] && [ $COUNT_FAIL_2 == 0 ];
    then
        echo "$INTERFACE_2 is in default and is working"
			

    elif [ $COUNT_FAIL_1 -ge $MAX_FAIL ] && [ $COUNT_FAIL_2 == 0 ]; # require another interface working
    then
        echo "COMD: Switch to route $GW_2"
        ROUTE_CHANGE "$INTERFACE_1" "$INTERFACE_2"
        COUNT_FAIL_1=0
    elif [ $COUNT_FAIL_2 -ge $MAX_FAIL ] && [ $COUNT_FAIL_1 == 0 ];
    then
        echo "COMD: Switch to route $GW_1"
        ROUTE_CHANGE "$INTERFACE_2" "$INTERFACE_1"
		# delete the first default route and then append to the tail
        COUNT_FAIL_2=0

	else
		echo "temporary failed"
		echo "$INTERFACE_1 fail: $COUNT_FAIL_1; $INTERFACE_2 fail: $COUNT_FAIL_2"
	fi
	
	sleep $INTERVAL_PING
done
