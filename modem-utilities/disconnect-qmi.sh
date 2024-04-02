#!/bin/bash

# Author: Chih-Yang Chen
# Description: disconnect the target INTERFACE of cellular module which uses qmi_wwan driver.
# input: -i [INTERFACE name] 
# output: NA
# Note: Neet to use dial.sh by Chih-Yang

source PATH_for_NTU_exp
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE]"
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi

path="$PATH_TEMP_DIR/temp"
wds_path="$path/temp-wds_$INTERFACE"
wdm=`(head -1 $path/$INTERFACE)`
wds_id=`(cat $wds_path | grep CID | awk '{print $2}' | sed 's/.$//' | sed 's/^.//')`
qmicli -d $wdm --device-open-proxy --wds-stop-network=disable-autoconnect --client-cid=$wds_id

ifconfig $INTERFACE  down
ifconfig $INTERFACE 0.0.0.0

