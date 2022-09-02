#!/bin/bash

#Author: Chih-Yang Chen
#function: use the mxat utility to set the band suport of target modem
#input:  -d [AT PORT] -l [LTE BAND] -e [ENDC NR BAND] 
#output: NA
helpFunction()
{
    echo ""
    echo "Usage: $0 -d [/dev/ttyUSBX] -l [LTE band combination] -e [ENDC NR Band combination]"
    exit 1 # Exit script after printing help
}
while getopts "d:l:e:" opt
do
    case "$opt" in
        d ) PORT="$OPTARG" ;;
        l ) LTE="$OPTARG" ;;
        e ) ENDC="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$PORT" ]
then
    echo "missing argument"
    helpFunction
fi

if [ -z "$LTE"] & [ -z "$ENDC" ]
then
    echo "current band setting"
    mxat -d $PORT -c at+qnwprefcfg=\"lte_band\"
    mxat -d $PORT -c at+qnwprefcfg=\"nsa_nr5g_band\"
fi

if [ ! -z "$LTE" ]
then
    mxat -d $PORT -c at+qnwprefcfg=\"lte_band\",$LTE
fi

if [ ! -z "$ENDC" ]
then
    mxat -d $PORT -c at+qnwprefcfg=\"nsa_nr5g_band\",$ENDC
fi


#echo $PORT
#echo $lte
