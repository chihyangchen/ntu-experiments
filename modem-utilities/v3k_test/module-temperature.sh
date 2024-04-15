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
        t ) delay="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ] 
then
    echo "missing argument"
    helpFunction
fi


capture()
{
    echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qtemp
	sensors
}
filename=$INTERFACE"_`(date +%Y-%m-%d_%H-%M-%S)`"
if [ -z $delay ]
then
    capture
else
    main_path="$TOP/modem_temperature"
    path="$main_path/at_log_quectel_`(date +%Y-%m-%d)`"
    if [ ! -d $main_path ]
        then
           ${SUDO} mkdir $main_path
    fi
    if [ ! -d $path ]
        then
           ${SUDO} mkdir $path
    fi
    if [ ! -d "$path/$INTERFACE" ]
        then
            ${SUDO} mkdir "$path/$INTERFACE"
    fi
    
    ${SUDO} touch "$TOP/temp/looping_$INTERFACE"
    while [ -f "$TOP/temp/looping_$INTERFACE" ] 
    do
        capture |${SUDO} tee -a "$path/$INTERFACE/$filename" 
        sleep $delay
#        tail -10 "$path/$INTERFACE/$filename"
    done
fi

