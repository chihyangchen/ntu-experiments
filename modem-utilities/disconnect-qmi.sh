#!/bin/bash

# Author: Chih-Yang Chen
# Description: disconnect the target interface of cellular module which uses qmi_wwan driver.
# input: -i [interface name] 
# output: NA
# Note: Neet to use dial.sh by Chih-Yang

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface]"
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
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

path="./temp"
wds_path="$path/temp-wds_$interface"
wdm=`(head -1 $path/$interface)`
wds_id=`(cat $wds_path | grep CID | awk '{print $2}' | sed 's/.$//' | sed 's/^.//')`
qmicli -d $wdm --device-open-proxy --wds-stop-network=disable-autoconnect --client-cid=$wds_id

ifconfig $interface  down
ifconfig $interface 0.0.0.0

