#!/bin/bash

#Author: Chih-Yang Chen
#input:  network interface name of usb modem
#output: network interface file with cdc-wdmX and the corresponding at command port inside

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] {-P [PATH]}"
    exit 1 # Exit script after printing help
}

while getopts "i:P:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        P ) path="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ]
then
    echo "missing argument"
    helpFunction
fi

wdm=`ls /sys/class/net/$interface/device/usbmisc/`
if [ -z "$wdm" ]
then
    echo "no $interface device"
    exit 1
fi

for i in $@ ;do
    case "$i" in
    wwan0)
        DEV_AT_PATH="serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if03-port0"
        ;;
    quectel0)
        DEV_AT_PATH="serial/by-id/usb-Quectel_RM500Q-GL_76857c8-if03-port0"
        ;;
    quectel1)
        DEV_AT_PATH="serial/by-id/usb-Quectel_RM500Q-GL_bc4587d-if03-port0"
        ;;
    quectel2)
        DEV_AT_PATH="serial/by-id/usb-Quectel_RM500Q-GL_5881b62f-if03-port0"
        ;;
    quectel3)
        DEV_AT_PATH="serial/by-id/usb-Quectel_RM500Q-GL_32b2bdb2-if03-port0"
        ;;
    esac
done

if [ -z "$path" ]
then
    echo "/dev/$wdm" > $interface
    echo "/dev/$DEV_AT_PATH" >> $interface
else
    if [ ! -d $path ]
    then
        mkdir $path
    fi
    echo "/dev/$wdm" > "$path/$interface"
    echo "/dev/$DEV_AT_PATH" >> "$path/$interface"
fi
