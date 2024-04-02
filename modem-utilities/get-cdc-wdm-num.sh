#!/bin/bash

#Author: Chih-Yang Chen
#input:  network INTERFACE name of usb modem
#output: network INTERFACE file with cdc-wdmX and the corresponding at command port inside
source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] "
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
#        P ) path="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi
TOP="$PATH_TEMP_DIR"
path="$TOP/temp"
wdm=`ls /sys/class/net/$INTERFACE/device/usbmisc/`
if [ -z "$wdm" ]
then
    echo "no $INTERFACE device"
    exit 1
fi

GET_DM_PATH $INTERFACE


# Fixed the save path
if [ ! -d $path ]
then
        mkdir $path
fi
    echo "/dev/$wdm" > "$path/$INTERFACE"
    echo "$DEV_DM_PATH" >> "$path/$INTERFACE"
