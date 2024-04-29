#!/bin/bah

source PATH_for_NTU_exp
helpFunction()
{
    echo ""
    echo "Usage: $0 [ -r (-T INTERVAL) ] or [ -w -i [INTERFACE] (-l) (-f) (-p) (-s) (-t)]"
    echo "-r: Regular report"
    echo ""
    echo "-w: WARNING"
    echo "-i: INTERFACE: network INTERFACE"
	echo "-l: Loss connection"
    echo "-f: Fight mode toggling"
    echo "-p: pwr gpio toggling"
    echo "-s: SIM error"
    echo "-t: thermal"
    echo ""
    exit 1 # Exit script after printing help
}
while getopts "i:rT:wlfpst" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        r ) FUNC="REGULAR" ;;
        w ) FUNC="WARNING" ;;
        l ) TYPE="LOST_CONNECTION" ;;
        f ) TYPE="FLIGHT_MODE_TOGGLING" ;;
        p ) TYPE="PWR_GPIO_TOGGLING" ;;
        s ) TYPE="SIM_ERROR" ;;
        t ) TYPE="THERMAL" ;;
        ? ) helpFunction ;;
    esac
done

if  [ -z "$FUNC" ]
then
    echo "missing argument"
    helpFunction
fi

if [ "$FUNC" == "WARNING" ]
then
	if [ -z "$TYPE" ] || [ -z "$INTERFACE" ]
	then
    	echo "missing argument"
		echo "Require INTERFACE and WARNING TYPE"
    	helpFunction
	fi
fi
#echo "$FUNC"
#echo "$TYPE"


#exit 0
INTERFACE_1="m21"
INTERFACE_2="m22"
DEV=`(ls $PATH_TEMP_DIR/Metro*)` > /dev/null 2>&1

if [ "$DEV" == "$PATH_TEMP_DIR/Metro#1" ];
then
    INTERFACE_1="m11"
    INTERFACE_2="m12"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#2" ];
then
    INTERFACE_1="m21"
    INTERFACE_2="m22"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#3" ];
then
    INTERFACE_1="m31"
    INTERFACE_2="m32"
elif [ "$DEV" == "$PATH_TEMP_DIR/Metro#4" ];
then
    INTERFACE_1="m41"
    INTERFACE_2="m42"
fi



function operation_system_log() {
# Time
	echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
	echo "reason,update"
# System temperature
	sensors
# Modem 1 temperature
	echo "device,$INTERFACE_1"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE_1 -c at+qtemp
# Modem 2 termperature
	echo "device,$INTERFACE_2"
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE_2 -c at+qtemp

}
function system_log() {
		operation_system_log
}
function operation_warning_log() {
# TIME
	echo "time,`(date +%Y-%m-%d_%H-%M-%S)`"
# REASON
	echo "reason,$TYPE"
# SYSTEM temperature
	sensors
# Modem temperature
	${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+qtemp
# FILE: warning_INTERFACE.txt
}

function warning_log() {
	operation_warning_log
}
if [ "$FUNC" == "WARNING" ]
then
	warning_log
else
	system_log #> /dev/null
fi
