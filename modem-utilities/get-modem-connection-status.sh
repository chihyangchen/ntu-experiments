#!/bin/bash

#Author: Chih-Yang Chen
#function: use the mxat utility to set the band suport of target modem
#           will auto select the target INTERFACE dev    
#input:  -i [INTERFACE] -l [LTE BAND] -e [ENDC NR BAND] 
#output: NA
source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh

SUDO=sudo

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] "
    echo "e.g. sudo ./band-setting.sh -i [INTERFACE] "
    exit 1 # Exit script after printing help
}
while getopts "i:l:e:" opt
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

GET_AT_PATH $INTERFACE

    echo "current modem status"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cops?
#    mxat -d $DEV_AT_PATH -c at+cops?
	echo "connection status"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qeng=\"servingcell\"
#    mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\"



#echo $PORT
#echo $lte
