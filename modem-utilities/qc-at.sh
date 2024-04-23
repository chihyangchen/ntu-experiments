#!/bin/bash

source PATH_for_NTU_exp

TOP=$PATH_TEMP_DIR
source $PATH_UTILS/quectel-path.sh
#echo $PATH_UTILS
SUDO=sudo
AT_TIMEOUT=10000

CHECK_temp_dir

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] -c [at command]"
    echo "INTERFACE: network INTERFACE"
    echo "at command: eg. at+cpin?"
    exit 1 # Exit script after printing help
}

while getopts "i:c:t:s" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        c ) cmd="$OPTARG" ;;
        t ) AT_TIMEOUT="$OPTARG" ;;
        s ) SMS="USING" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ] || [ -z "$cmd" ]
then
    echo "missing argument"
    helpFunction
fi

LOCK_FILE=$TOP/temp/$INTERFACE.lock
SMS_LOCK_FILE=$TOP/temp/sms-$INTERFACE.lock

GET_AT_PATH $INTERFACE
if ! [ "$SMS" == "USING" ]
then
	while [ -f $SMS_LOCK_FILE ]; 
	do
		echo "SMS is sending. please wait!"
		sleep 0.5 
	done
fi

while [ -f $LOCK_FILE ]; 
do
	echo "device port is occupied!"
	sleep 0.5 
done
#else
	${SUDO} touch $LOCK_FILE
	${SUDO} mxat -d $DEV_AT_PATH -c $cmd -t $AT_TIMEOUT
	${SUDO} rm -f ${LOCK_FILE}
#fi
