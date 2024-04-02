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


GET_AT_PATH $INTERFACE

while [  -z $DEV_AT_PATH ] ||  [ ! -e $DEV_AT_PATH  ];
do
#    echo "$INTERFACE module exists."
#else
	echo "No related module"
	sleep 0.2
done

while [ "$result" != "${isOK}" ]
do
	status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c AT)`

	for i in ${status[@]};
	do
		sts+=($i)
	done
		result=${sts[1]}
	unset sts

	if [ "$result" == "${isOK}" ]
	then
		echo "module AT port ready"
	else
		echo "module AT port not ready"
		sleep 0.2
	fi
done
