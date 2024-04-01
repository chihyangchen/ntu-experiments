#!/bin/bash

source ./quectel-path.sh
TOP=/home/moxa

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] -c [at command]"
    echo "interface: network interface"
    echo "at command: eg. at+cpin?"
    exit 1 # Exit script after printing help
}

while getopts "i:c:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        c ) cmd="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$interface" ] || [ -z "$cmd" ]
then
    echo "missing argument"
    helpFunction
fi

if [ ! -d $TOP/temp ]; then
	echo "Directory does not exist."
	mkdir $TOP/temp
fi
LOCK_FILE=$TOP/temp/$interface.lock

GET_AT_PATH $interface

if [ -f $LOCK_FILE ]; then
	echo "device port is occupied!"
	sleep 1
else
	touch $LOCK_FILE
	mxat -d $DEV_AT_PATH -c $cmd -t 10000
	rm -f ${LOCK_FILE}
fi
