#!/bin/bash

source PATH_for_NTU_exp
V3K_USE="v3k_test"
SUDO=sudo

lsmod | grep gpio_pca953x > /dev/null 2>&1
if [  $? ]
then
    ${SUDO} modprobe gpio_pca953x
	echo "modprobe gpio_pca953x"
fi

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
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


#insmod /home/moxa/young/v3000_package/repo/moxa-gpio-pca953x-driver/gpio-pca953x.ko
GET_GPIO_SLOT $INTERFACE

${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -p high
sleep 0.05
# use the SIM of side B
${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -i 2
sleep 0.05
${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -t high
${SUDO} ${PATH_UTILS}/${V3K_USE}/mx-m2b-module-ctl -s ${SLOT} -r high

$PATH_UTILS/check_quectel_exist.sh -i $INTERFACE
#while true; do
#	val=$(${PATH_UTILS}/mx-m2b-module-ctl -s 1 -m | grep "FN980" | cut -d '=' -f 2)
#	if [ "$val" == "1" ]; then
#		break
#	fi
#	sleep 1
#done
