#!/bin/bash

source PATH_for_NTU_exp
SUDO=sudo
helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] "
    echo "INTERFACE: INTERFACE name eg. wwan0"
    echo "PATH: path to save the temp file"
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
#        s ) apn="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ] 
then
    echo "missing argument"
    helpFunction
fi

path="$PATH_TEMP_DIR/temp"
wds_path="$path/temp-wds_$INTERFACE"
wds_ip_path="$path/temp-ip_$INTERFACE"
wds_ip_filter="$path/temp-ip-setting_$INTERFACE"
wdm=`(head -1 $PATH_TEMP_DIR/temp/$INTERFACE)`
mux="1"
apn="internet"
:> $wds_path
:> $wds_ip_path
:> $wds_ip_filter

echo 'Y' | ${SUDO} tee /sys/class/net/${INTERFACE}/qmi/raw_ip

(${SUDO} qmicli -p -d $wdm --client-no-release-cid --wds-noop) > $wds_path
while [ ! -s "$wds_path" ]
do
	echo "re-allocate the wds resource"
	sleep 1
	(${SUDO} qmicli -p -d $wdm --client-no-release-cid --wds-noop) > $wds_path
done
echo "Allocate wds resource succcess"
wds_id=`(cat $wds_path | grep CID | awk '{print $2}' | sed 's/.$//' | sed 's/^.//')`

${SUDO} qmicli -d $wdm --device-open-proxy --wds-start-network="ip-type=4,apn=$apn" --client-cid=$wds_id --client-no-release-cid
(${SUDO} qmicli -p -d $wdm --wds-get-current-settings --client-cid=$wds_id --client-no-release-cid) > $wds_ip_path

$PATH_UTILS/read-setting.py $wds_ip_path $wds_ip_filter
ip=`(cat $wds_ip_filter | head -1)`
mask=`(cat $wds_ip_filter | head -2 | tail -1)`

${SUDO} ifconfig $INTERFACE up
${SUDO} ifconfig $INTERFACE $ip netmask $mask
#udhcpc -f -n -q -t 5 -i wwan0

