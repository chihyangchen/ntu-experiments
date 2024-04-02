#!/bin/bash
## DO not use

# Author: Chih-Yang Chen
# Description: 
#       acquire the serving/neighbour cell info from target at command port 
#       loop if add delay -t argument
# input: -i INTERFACE -t delay time
# output: at command information
echo "Do NOT USE"
exit 0

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
TOP="$PATH_TEMP_DIR"

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] {-t [delay sec]}"
    echo "INTERFACE: network INTERFACE"
    echo "sleep time: wait time of each information capture"
    exit 1 # Exit script after printing help
}

while getopts "i:t:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        t ) delay="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ] 
then
    echo "missing argument"
    helpFunction
fi

GET_AT_PATH $INTERFACE
wdm=`(head -1 $TOP/temp/$INTERFACE)`

capture()
{
    echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
    mxat -d $DEV_AT_PATH -c at+qeng=\"servingcell\" -t 3000
    mxat -d $DEV_AT_PATH -c at+qeng=\"neighbourcell\" -t 3000
    qmicli -p -d $wdm --nas-get-cell-location-info
}
filename=$INTERFACE"_`(date +%Y-%m-%d_%H-%M-%S)`"
if [ -z $delay ]
then
    capture
else
    path="at_log_quectel_`(date +%Y-%m-%d)`"
    if [ ! -d $path ]
        then
            mkdir $path
    fi
    if [ ! -d "$path/$INTERFACE" ]
        then
            mkdir "$path/$INTERFACE"
    fi
    
    touch ./looping
    while [ -f ./looping ] 
    do
        capture >> "$path/$INTERFACE/$filename"
        sleep $delay
#        tail -10 "$path/$INTERFACE/$filename"
    done
fi

