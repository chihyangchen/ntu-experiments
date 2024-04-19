#!/bin/bash

	
SUDO=sudo
V3K_USE="v3k_test"

lsmod | grep gpio_pca953x > /dev/null 2>&1 
if [ $? ]
then
	${SUDO} modprobe gpio_pca953x
fi

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
source $PATH_UTILS/AT_CHECK

SUDO=sudo
sts=()
result=""
COUNT=0
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
GET_GPIO_SLOT $INTERFACE

${SUDO} rm -rf $PATH_TEMP_DIR/temp/temp*$INTERFACE

if [ ! -e $DEV_AT_PATH  ]
then
	echo "module is power down"
	exit 0
fi

${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -t low

while [  -e $DEV_AT_PATH  ];
do
#    echo "$INTERFACE module exists."
#else
    echo "module is still alive"
    sleep 0.2
	let COUNT+=1
	if [ $COUNT -gt 150 ]
	then
		break
	fi
done


${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -r low
${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -p low

