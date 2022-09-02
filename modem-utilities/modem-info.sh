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
    echo "Usage: $0 -d [/dev/ttyUABX] {-t [delay]}"
    echo "/dev/ttyUSBX: X is the num of device"
    echo "sleep time: wait time of each information capture"
    exit 1 # Exit script after printing help
}

while getopts "d:t:" opt
do
    case "$opt" in
        d ) dev="$OPTARG" ;;
        t ) delay="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$dev" ] 
then
    echo "missing argument"
    helpFunction
fi

capture()
{
    #FIXME: add the current timestamp
    mxat -d $dev -c at+qeng=\"servingcell\" -t 3000
    mxat -d $dev -c at+qeng=\"neighbourcell\" -t 3000
       
}

if [ -z $delay ]
then
    capture
else
    while true 
    do
        capture
        sleep $delay 
    done
fi
