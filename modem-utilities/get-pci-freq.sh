#!/bin/bash

# Author: Sheng-Ru Zeng
# Description: 
#       acquire the serving cell pci and earfcn/arfcn from target at command port 
#       loop if add delay -t argument
# input: -i interface -t delay time
# output: at command information

source ./quectel-path.sh

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] {-t [delay sec]}"
    echo "interface: network interface"
    echo "sleep time: wait time of each information capture"
    exit 1 # Exit script after printing help
}

while getopts "i:t:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        t ) delay="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ] 
then
    echo "missing argument"
    helpFunction
fi

GET_AT_PATH $interface
wdm=`(head -1 ./temp/$interface)`

mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\"