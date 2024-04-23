#!/bin/bash

source PATH_for_NTU_exp

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] "
    echo "INTERFACE: network INTERFACE"
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


# default ATE1
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c ATE1 -t 5000)` > /dev/null 2>&1
# default SMS in text mode 
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c AT+CMGF=1 -t 5000)` > /dev/null 2>&1
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c AT+CSCS=\"GSM\" -t 5000)` > /dev/null 2>&1
# default band
