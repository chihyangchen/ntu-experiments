#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/quectel-path.sh
TOP=$PATH_TEMP_DIR
SUDO=sudo

CHECK_temp_dir

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] -n [PHONE_NUMBER] -m [MESSAGE]"
    echo "INTERFACE: network INTERFACE"
    echo "at command: eg. at+cpin?"
    exit 1 # Exit script after printing help
}
while getopts "i:n:m:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        n ) PHONE="$OPTARG" ;;
        m ) MESSAGE="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ] || [ -z "$PHONE" ] || [ -z "$MESSAGE" ]
then
    echo "missing argument"
    helpFunction
fi



SMS_LOCK_FILE=$TOP/temp/sms-$INTERFACE.lock

${SUDO} touch $SMS_LOCK_FILE

`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c AT+CMGS=\"$PHONE\" -s)`  > /dev/null 2>&1
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c $MESSAGE -s)` > /dev/null 2>&1
`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c '\032' -s)` > /dev/null 2>&1

${SUDO} rm -f ${SMS_LOCK_FILE}
