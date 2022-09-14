#!/bin/bash

source ./quectel-path.sh

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] -c [at command]"
    echo "interface: network interface"
    echo "at command: eg. at+cpin?"
    exit 1 # Exit script after printing help
}

while getopts "i:c:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        c ) cmd="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$interface" ] || [ -z "$cmd" ]
then
    echo "missing argument"
    helpFunction
fi
GET_AT_PATH $interface

mxat -d $DEV_AT_PATH -c $cmd
