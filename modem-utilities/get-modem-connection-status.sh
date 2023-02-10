#!/bin/bash

#Author: Chih-Yang Chen
#function: use the mxat utility to set the band suport of target modem
#           will auto select the target interface dev    
#input:  -i [interface] -l [LTE BAND] -e [ENDC NR BAND] 
#output: NA
source ./quectel-path.sh
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] "
    echo "e.g. sudo ./band-setting.sh -i [interface] "
    exit 1 # Exit script after printing help
}
while getopts "i:l:e:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ]
then
    echo "missing argument"
    helpFunction
fi

GET_AT_PATH $interface

    echo "current modem status"
    mxat -d $DEV_AT_PATH -c at+cops?
	echo "connection status"
    mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\"



#echo $PORT
#echo $lte
