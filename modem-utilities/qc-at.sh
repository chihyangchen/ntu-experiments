#!/bin/bash

source PATH_for_NTU_exp

TOP=$PATH_TEMP_DIR
source $PATH_UTILS/quectel-path.sh
#echo $PATH_UTILS
SUDO=sudo
AT_TIMEOUT=10000

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] -c [at command]"
    echo "INTERFACE: network INTERFACE"
    echo "at command: eg. at+cpin?"
    exit 1 # Exit script after printing help
}

while getopts "i:c:t:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        c ) cmd="$OPTARG" ;;
        t ) AT_TIMEOUT="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ] || [ -z "$cmd" ]
then
    echo "missing argument"
    helpFunction
fi

if [ ! -d $TOP/temp ]; then
	echo "Directory does not exist."
	mkdir $TOP/temp
fi
LOCK_FILE=$TOP/temp/$INTERFACE.lock

GET_AT_PATH $INTERFACE

if [ -f $LOCK_FILE ]; then
	echo "device port is occupied!"
	sleep 0.5 
else
	touch $LOCK_FILE
	${SUDO} mxat -d $DEV_AT_PATH -c $cmd -t $AT_TIMEOUT
	rm -f ${LOCK_FILE}
fi
