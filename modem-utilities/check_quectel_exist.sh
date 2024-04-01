#!/bin/bash

# The value can only be defined in quectel=path.sh
source quectel-path.sh
source AT_CHECK
SUDO=sudo
sts=()
result=""

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] "
    echo "interface: network interface"
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$interface" ]
then
    echo "missing argument"
    helpFunction
fi


GET_AT_PATH $interface

while [ ! -e $DEV_AT_PATH ];
do
#    echo "$interface module exists."
#else
	echo "No related module"
	sleep 0.2
done

while [ "$result" != "${isOK}" ]
do
	status=`(${SUDO} ./qc-at.sh -i $interface -c AT)`

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
