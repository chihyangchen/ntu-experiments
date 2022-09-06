#!/bin/bash

# Author: Chih-Yang Chen
# Description: 
#       acquire the serving/neighbour cell info from target at command port 
#       loop if add delay -t argument
# input: -d /dev/ttyUSBX -t delay time
# output: at command information

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] {-t [delay sec]}"
    echo "interface: network interface"
    echo "sleep time: wait time of each information capture"
    exit 1 # Exit script after printing help
}

while getopts "i:t:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        t ) delay="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ] 
then
    echo "missing argument"
    helpFunction
fi


for i in $@ ;do
    case "$i" in
    wwan0)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if03-port0"
        ;;
    quectel0)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_76857c8-if03-port0"
        ;;
    quectel1)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_bc4587d-if03-port0"
        ;;
    quectel2)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_5881b62f-if03-port0"
        ;;
    quectel3)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_32b2bdb2-if03-port0"
        ;;
    esac
done

capture()
{
    echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
    mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\" -t 3000
    mxat -d $DEV_AT_PATH -c at+qeng=\"neighbourcell\" -t 3000
       
}
filename=$interface"_`(date +%Y-%m-%d_%H-%M-%S)`"
if [ -z $delay ]
then
    capture
else
    path="at_log_quectel_`(date +%Y-%m-%d)`"
    if [ ! -d $path ]
        then
            mkdir $path
    fi
    if [ ! -d "$path/$interface" ]
        then
            mkdir "$path/$interface"
    fi
    
    touch ./looping
    while [ -f ./looping ] 
    do
        capture >> "$path/$interface/$filename"
        sleep $delay
#        tail -10 "$path/$interface/$filename"
    done
fi
