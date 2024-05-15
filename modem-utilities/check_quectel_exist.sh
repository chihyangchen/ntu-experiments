#!/bin/bash

# The value can only be defined in quectel=path.sh
source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
source $PATH_UTILS/AT_CHECK

SUDO=sudo
sts=()
result=""

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
INTERVAL=0.5
COUNT=0
FAIL_TRY=180

GET_AT_PATH $INTERFACE

echo "Start to check if $INTERFACE exists. Please wait."
while [  -z $DEV_AT_PATH ] ||  [ ! -e $DEV_AT_PATH  ];
do
#    echo "$INTERFACE module exists."
#else
	echo "No related module" > /dev/null 2>&1
	sleep $INTERVAL
	let COUNT+=1
	if [ $COUNT -gt $FAIL_TRY ]
	then
		echo "Module may be failed: $INTERFACE"
		exit 1
	fi
done

COUNT=0
while [ "$result" != "${isOK}" ]
do
	status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c AT -t 5000)`

	for i in ${status[@]};
	do
		sts+=($i)
	done
		result=${sts[1]}
	unset sts

	if [ "$result" == "${isOK}" ]
	then
		echo "$INTERFACE module AT port ready"
	else
		echo "$INTERFACE module AT port not ready"
		let COUNT+=1
		sleep $INTERVAL
	fi
	if [ $COUNT -gt $FAIL_TRY ]
	then
		exit 1
	fi
done
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c ATE1 -t 5000)` > /dev/null 2>&1
