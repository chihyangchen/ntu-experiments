#!/bin/bash

source ./AT_CHECK

SUDO=sudo
INTERFACE=m21
COUNT=0
sts=()
result=$COPS0

while [ $result == $COPS0 ] || [ $result == $COPS2 ];
do

	status=`(${SUDO} ./qc-at.sh -i $INTERFACE -c at+cops?)`

	for i in ${status[@]}; 
	do
		sts+=($i)
	done
	result=${sts[2]}
	unset sts

	if  [ $result == $COPS0 ] || [ $result == $COPS2 ] ; then
		echo "wait for registration"
		sleep 6
		let COUNT+=1
	else
		echo "success"
	fi

	if [ $COUNT -gt 9 ]; then
		COUNT=0
		echo "toggle cfun 0/1"
		${SUDO} ./qc-at.sh -i $INTERFACE -c at+cfun=0
		${SUDO} ./qc-at.sh -i $INTERFACE -c at+cfun=1
	fi

done
