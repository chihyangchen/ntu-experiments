#!/bin/bash

#Author: Chih-Yang Chen
#function: use the mxat utility to set the band suport of target modem
#           will auto select the target interface dev    
#input:  -i [interface] -l [LTE BAND] -e [ENDC NR BAND] 
#output: NA
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] -l [LTE band combination] -e [ENDC NR Band combination]"
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
