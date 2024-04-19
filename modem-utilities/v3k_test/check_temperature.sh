#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh

TOP="$PATH_TEMP_DIR"
TEMP_DIR=$TOP/temp
V3k_USE="$PATH_UTILS/v3k_test"

SUDO=sudo

THRESHOLD=40

capture()
{
    echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
#    ${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qtemp
    sensors
}

filename="monitor_temperature"
capture |${SUDO} tee "$TEMP_DIR/$filename" > /dev/null 2>&1

${SUDO} $V3k_USE/temperature_filter_when_error.py  $TEMP_DIR/$filename  $TEMP_DIR/

TEMPERATURE_CORE0=`(cat $TEMP_DIR/monitor_core0_temperature)`
TEMPERATURE_CORE1=`(cat $TEMP_DIR/monitor_core1_temperature)`
TEMPERATURE_CORE2=`(cat $TEMP_DIR/monitor_core2_temperature)`
TEMPERATURE_CORE3=`(cat $TEMP_DIR/monitor_core3_temperature)`
TEMPERATURE_NVME=`(cat $TEMP_DIR/monitor_nvme_temperature)`


if [ $TEMPERATURE_NVME -gt $THRESHOLD ] || [ $TEMPERATURE_CORE0 -gt $THRESHOLD ] || [ $TEMPERATURE_CORE1 -gt $THRESHOLD ] || [ $TEMPERATURE_CORE2 -gt $THRESHOLD ] || [ $TEMPERATURE_CORE3 -gt $THRESHOLD ] || [ $TEMPERATURE_CORE3 -gt $THRESHOLD ] 
then
	echo "curent termperatuire of NVME: $TEMPERATURE_NVME"
	echo "curent termperatuire of CORE0: $TEMPERATURE_CORE0"
	echo "curent termperatuire of CORE1: $TEMPERATURE_CORE1"
	echo "curent termperatuire of CORE2: $TEMPERATURE_CORE2"
	echo "curent termperatuire of CORE3: $TEMPERATURE_CORE3"
	exit 1
fi

