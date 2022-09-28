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
    echo "Usage: $0 -i [interface] -l [LTE band combination] -e [ENDC NR Band combination]"
    echo "e.g. sudo ./band-setting.sh -i [interface] -l 1:2:3:4  -e 77:78:79"
    exit 1 # Exit script after printing help
}
while getopts "i:l:e:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        l ) LTE="$OPTARG" ;;
        e ) ENDC="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ]
then
    echo "missing argument"
    helpFunction
fi

GET_AT_PATH $interface

if [ -z "$LTE"] && [ -z "$ENDC" ]
then
    echo "current band setting"
    mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"lte_band\"
    mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"nsa_nr5g_band\"
fi

if [ ! -z "$LTE" ]
then
    mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"lte_band\",$LTE
fi

if [ ! -z "$ENDC" ]
then
    mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"nsa_nr5g_band\",$ENDC
fi


#echo $PORT
#echo $lte
