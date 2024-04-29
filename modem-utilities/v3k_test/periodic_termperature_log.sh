#!/bin/bash

# Author: Chih-Yang Chen
# Description:
#       acquire the module temperature from command port
#       loop if add delay -t argument
# input: -i INTERFACE -t delay time
# output: at command information
#echo "Do NOT USE"
#exit 0

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh

TOP="$PATH_TEMP_DIR"
LOG_POSITION="/mnt"
SUDO=sudo

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] {-t [delay sec]}"
    echo "INTERFACE: network INTERFACE"
    echo "sleep time: wait time of each information capture"
    exit 1 # Exit script after printing help
}

while getopts "i:t:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        t ) INTERVAL="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi

PATH_OPERATION_LOG="/mnt"
DIR_OPERATION_LOG="system_log"
if [ ! -d "$PATH_OPERATION_LOG/$DIR_OPERATION_LOG" ]
then
    ${SUDO} mkdir "$PATH_OPERATION_LOG/$DIR_OPERATION_LOG"
fi

FILENAME_OPERATION_LOG="op_log_"`(date +%Y-%m-%d)`".txt"
PATH_WARNING_LOG="warning_$INTERFACE.txt"
LOG_PATH_FILENAME="$PATH_OPERATION_LOG/$DIR_OPERATION_LOG/$FILENAME_OPERATION_LOG"
if ! [ -z $INTERVAL ]
then
	${SUDO}	touch "$PATH_TEMP_DIR/temp/CONT_LOG"
fi

while [ -f "$PATH_TEMP_DIR/temp/CONT_LOG" ]
do
	${SUDO}	bash log_func.sh -r | ${SUDO} tee -a $LOG_PATH_FILENAME
	sleep $INTERVAL
done






