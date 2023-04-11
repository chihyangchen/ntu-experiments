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
    echo "Usage: $0 -i [interface] -m [Network Search Mode Configuration]"
    echo "e.g. sudo ./band-setting.sh -i [interface] -m auto"
    echo "e.g. sudo ./band-setting.sh -i [interface] -m nr5g"
    echo "e.g. sudo ./band-setting.sh -i [interface] -m lte"
    echo "e.g. sudo ./band-setting.sh -i [interface] -m wcdma"
    echo "e.g. sudo ./band-setting.sh -i [interface] -m rat1:rat2:...ratN"
    exit 1 # Exit script after printing help
}
while getopts "i:m:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        # l ) LTE="$OPTARG" ;;
        # e ) ENDC="$OPTARG" ;;
        # w ) WCDMA="$OPTARG" ;;
        m ) mode="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ]
then
    echo "missing argument"
    echo "auto wcdma lte nr5g rat1:rat2:...ratN"
    helpFunction
fi

GET_AT_PATH $interface

if [ -z "$mode" ]
then
    echo "current modem status"
    mxat -d $DEV_AT_PATH -c at+cops?
	echo "connection status"
    mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\"
fi

if [ ! -z "$mode" ]
then
    mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"mode_pref\",$mode
fi
