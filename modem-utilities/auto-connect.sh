#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/AT_CHECK

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] (-d)"
    exit 1 # Exit script after printing help
}

while getopts "i:d" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        d ) DWG="0.0.0.0" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi


SUDO=sudo
COUNT=0
sts=()
CHECK_INTERVAL=6
VAL_TO_CFUN=9

function SIM_CHECK() {
	sts=()
	status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cpin?)`
    	for i in ${status[@]};
    	do
        	sts+=($i)
    	done
    res=${sts[4]}
    echo "$result"
    unset sts
	if [ "$res" != "$isOK" ]
	then
    	echo "Something is wrong with SIM"
    	return 1 
	fi
}

function CFUN_TOGGLE() {

	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cfun=0
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cfun=1

}

SIM_CHECK
if [  $? != 0 ]
then
	CFUN_TOGGLE
	sleep 5 # delay for SIM enable when toggling
	SIM_CHECK
	if [  $? != 0 ]
	then
    	exit 0
	fi
fi


result=$COPS0

while [ $result == $COPS0 ] || [ $result == $COPS2 ];
do

	status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cops?)`
#	echo $status
	for i in ${status[@]}; 
	do
		sts+=($i)
	done
	result=${sts[2]}
	unset sts

	if  [ $result == $COPS0 ] || [ $result == $COPS2 ] ; then
		echo "wait for registration"
		sleep $CHECK_INTERVAL
		let COUNT+=1
	else
		echo "success"
		### COMMAND to do the dial
		if [ "$DWG" != "" ]
		then
			$PATH_UTILS/dial-qmi.sh -i $INTERFACE -d
		else
			$PATH_UTILS/dial-qmi.sh -i $INTERFACE
		fi
		exit 0
	fi

	if [ $COUNT -gt $VAL_TO_CFUN ]; then
		COUNT=0
		echo "toggle cfun 0/1"
		CFUN_TOGGLE
#		SIM_CHECK
#		if [  $? != 0 ]
#		then
#			break
#		fi
	fi

done
