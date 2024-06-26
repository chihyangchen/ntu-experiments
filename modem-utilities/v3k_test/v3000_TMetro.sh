#!/bin/bash


source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh

V3k_USE="v3k_test"
SUDO=sudo
INTERFACE_1=""
INTERFACE_2=""

DEV=`(ls $PATH_TEMP_DIR/Metro*)` > /dev/null 2>&1
#echo "$DEV"
if [ $? != 0 ];
then
	echo "Need to add a file Metro#X in ~/"
	echo "X is for 1 to 4, depends on the V3k device" 
	exit 0
fi

if [ "$DEV" == "$PATH_TEMP_DIR/Metro#1" ];
then
	echo "Metro#1"
	INTERFACE_1="m11"
	INTERFACE_2="m12"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#2" ];
then
	echo "Metro#2"
	INTERFACE_1="m21"
	INTERFACE_2="m22"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#3" ];
then
	echo "Metro#3"
	INTERFACE_1="m31"
	INTERFACE_2="m32"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#4" ];
then
	echo "Metro#4"
	INTERFACE_1="m41"
	INTERFACE_2="m42"
fi

echo "$INTERFACE_1"
echo "$INTERFACE_2"

if [ "$1" == "START" ]
then
	echo "mount ssd"
	${SUDO} mount /dev/sda1 $PATH_TEMP_DIR/my_SATA
	${SUDO} chown moxa:moxa $PATH_TEMP_DIR/my_SATA
	sleep 3
	${SUDO} modprobe drivetemp
	echo "start enabling m.2 slots"
	${SUDO} rm -f $PATH_TEMP_DIR/temp/* 
	# slot 1 enable &
	${SUDO} $PATH_UTILS/$V3k_USE/v3000_power_on_5g_slot.sh -i $INTERFACE_1 &
	# slot 2 enable &
	${SUDO} $PATH_UTILS/$V3k_USE/v3000_power_on_5g_slot.sh -i $INTERFACE_2 &
	wait
	${SUDO} $PATH_UTILS/$V3k_USE/module-default-setting.sh -i $INTERFACE_1  
	${SUDO} $PATH_UTILS/$V3k_USE/module-default-setting.sh -i $INTERFACE_2 
	# slot 1 connect &
	${SUDO} $PATH_UTILS/auto-connect.sh -i $INTERFACE_1 -d 
	wait
	# slot 2 connect
	${SUDO} $PATH_UTILS/auto-connect.sh -i $INTERFACE_2
	# Restart the VPN Process
	${SUDO} systemctl restart zerotier-one.service
	#SYSTEM GPS enable
	#Enable GPS port to gpsd
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE_1 -c at+qgps=1 
	GET_GPS_PATH $INTERFACE_1
	${SUDO} gpsd -n $DEV_GPS_PATH
 
elif [ "$1" == "STOP" ]
then
	echo "stop functions of m.2 slots"
	# slot 1 disconnect
	${SUDO} $PATH_UTILS/disconnect-qmi.sh -i $INTERFACE_1 &
	# slot 2 disconnect
	${SUDO} $PATH_UTILS/disconnect-qmi.sh -i $INTERFACE_2 &
	wait
	# slot 1 disable
	${SUDO} $PATH_UTILS/$V3k_USE/v3000_power_off_5g_slot.sh -i $INTERFACE_1 &
	# slot 2 disable
	${SUDO} $PATH_UTILS/$V3k_USE/v3000_power_off_5g_slot.sh -i $INTERFACE_2
	wait
	${SUDO} sync
	sleep 3
	${SUDO} umount $PATH_TEMP_DIR/my_SATA

	${SUDO} rm -f $PATH_TEMP_DIR/temp/* 
fi
