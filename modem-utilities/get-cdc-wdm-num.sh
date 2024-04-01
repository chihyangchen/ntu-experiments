#!/bin/bash

#Author: Chih-Yang Chen
#input:  network interface name of usb modem
#output: network interface file with cdc-wdmX and the corresponding at command port inside
source ./quectel-path.sh
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] "
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
#        P ) path="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ]
then
    echo "missing argument"
    helpFunction
fi
TOP=/home/moxa
path="$TOP/temp"
wdm=`ls /sys/class/net/$interface/device/usbmisc/`
if [ -z "$wdm" ]
then
    echo "no $interface device"
    exit 1
fi

GET_DM_PATH $interface

#for i in $@ ;do
#    case "$i" in
#    wwan0)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if00-port0"
#        ;;
#    wwan1)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_ed1c8b2e-if00-port0"
#        ;;
#    qc00)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_76857c8-if00-port0"
#        ;;
#    qc01)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_bc4587d-if00-port0"
#        ;;
#    qc02)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_5881b62f-if00-port0"
#        ;;
#    qc03)
#        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_32b2bdb2-if00-port0"
#        ;;
#    esac
#done

#if [ -z "$path" ]
#then
#    echo "/dev/$wdm" > $interface
#    echo "/dev/$DEV_AT_PATH" >> $interface
#else
# Fixed the save path
if [ ! -d $path ]
then
        mkdir $path
fi
    echo "/dev/$wdm" > "$path/$interface"
    echo "$DEV_DM_PATH" >> "$path/$interface"
#fi
