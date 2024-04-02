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
    echo "Usage: $0 -i [INTERFACE] -l [LTE band combination] -e [ENDC NR Band combination]"
    echo "e.g. sudo ./band-setting.sh -i [INTERFACE] -l 1:2:3:4  -e 77:78:79"
    exit 1 # Exit script after printing help
}
while getopts "i:l:e:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        l ) LTE="$OPTARG" ;;
        e ) ENDC="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi

GET_AT_PATH $INTERFACE

if [ -z "$LTE"] && [ -z "$ENDC" ]
then
    echo "current band setting"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qnwprefcfg=\"lte_band\"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qnwprefcfg=\"nsa_nr5g_band\"
#	mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"lte_band\"
#	mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"nsa_nr5g_band\"
fi

if [ ! -z "$LTE" ]
then
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qnwprefcfg=\"lte_band\",$LTE
#	mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"lte_band\",$LTE
fi

if [ ! -z "$ENDC" ]
then
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qnwprefcfg=\"nsa_nr5g_band\",$ENDC
#	mxat -d $DEV_AT_PATH -c at+qnwprefcfg=\"nsa_nr5g_band\",$ENDC
fi


#echo $PORT
#echo $lte
