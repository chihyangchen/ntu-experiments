#!/bin/bash

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [interface] "
    echo "interface: interface name eg. wwan0"
    echo "PATH: path to save the temp file"
    exit 1 # Exit script after printing help
}

while getopts "i:" opt
do
    case "$opt" in
        i ) interface="$OPTARG" ;;
#        s ) apn="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$interface" ] 
then
    echo "missing argument"
    helpFunction
fi

path="./temp"
wds_path="$path/temp-wds_$interface"
wds_ip_path="$path/temp-ip_$interface"
wds_ip_filter="$path/temp-ip-setting_$interface"
wdm=`(head -1 ./temp/$interface)`
mux="1"
apn="internet"
:> $wds_path
:> $wds_ip_path
:> $wds_ip_filter

echo Y > /sys/class/net/$interface/qmi/raw_ip


(qmicli -p -d $wdm --client-no-release-cid --wds-noop) > $wds_path
while [ ! -s "$wds_path" ]
do
	echo "re-allocate the wds resource"
	sleep 1
	(qmicli -p -d $wdm --client-no-release-cid --wds-noop) > $wds_path
done
echo "Allocate wds resource succcess"
wds_id=`(cat $wds_path | grep CID | awk '{print $2}' | sed 's/.$//' | sed 's/^.//')`

qmicli -d $wdm --device-open-proxy --wds-start-network="ip-type=4,apn=$apn" --client-cid=$wds_id --client-no-release-cid
(qmicli -p -d $wdm --wds-get-current-settings --client-cid=$wds_id --client-no-release-cid) > $wds_ip_path

./read-setting.py $wds_ip_path $wds_ip_filter
ip=`(cat $wds_ip_filter | head -1)`
mask=`(cat $wds_ip_filter | head -2 | tail -1)`

ifconfig $interface up
ifconfig $interface $ip netmask $mask
#udhcpc -f -n -q -t 5 -i wwan0

