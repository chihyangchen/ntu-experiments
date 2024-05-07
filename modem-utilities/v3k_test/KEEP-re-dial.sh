#!/bin/bash

source PATH_for_NTU_exp
TOP=$PATH_TEMP_DIR


helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE]"
    echo "INTERFACE: network INTERFACE"
    exit 1 # Exit script after printing help
}


#------------check argument--------------
while getopts "i:t:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        t ) AT_TIMEOUT="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi
#-----------end of check argument-------------

while true; do
    $PATH_UTILS/re-dial.sh -i $INTERFACE

    if [ "$?" == "1" ]; then
	echo "[KEEP re-dial]: restart re-dial script after 1min"
    	sleep 60
    fi
done
