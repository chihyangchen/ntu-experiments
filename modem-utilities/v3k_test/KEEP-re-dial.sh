#!/bin/bash
#flag -m for module 1 / -n for module 2"
#

source PATH_for_NTU_exp
TOP=$PATH_TEMP_DIR

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

echo "$INTERFACE_1" > /dev/null
echo "$INTERFACE_2" > /dev/null


helpFunction()
{
	echo ""
	echo "Usage: $0 [-m or -n]"
	exit 1 # Exit script after printing help
}


#------------check argument--------------
while getopts "mn" opt
do
	case "$opt" in
		m ) INTERFACE="$INTERFACE_1" ;;
		n ) INTERFACE="$INTERFACE_2" ;;
		? ) helpFunction ;;
	esac
done
if [ -z "$INTERFACE" ]
then
	echo "missing argument"
	echo "flag -m for module 1 / -n for module 2"
	helpFunction
fi
#-----------end of check argument-------------

while true; do
	$PATH_UTILS/re-dial.sh -i $INTERFACE

	if [ "$?" == "1" ]; then
		echo "[KEEP re-dial]: restart re-dial script after 1min"
		sleep 60
	fi
done
