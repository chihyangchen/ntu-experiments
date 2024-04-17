#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/AT_CHECK
SUDO=sudo

function PING_TEST(){
	ping 8.8.8.8 -I $1 -c 3 
	if [ $? != 0 ]
	then
		return 1
	else
		return 0
	fi
}

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE] (-d)"
    echo "INTERFACE: INTERFACE name eg. wwan0"
    echo "-d flag is set as the first default route. Otherwise, the route will be appended to the last"
    exit 1 # Exit script after printing help
}

while getopts "i:dc" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        d ) DGW="0.0.0.0" ;;
        c ) CHECK="do_check" ;;
        ? ) helpFunction ;;
    esac
done

if [ -z "$INTERFACE" ] 
then
    echo "missing argument"
    helpFunction
fi

sts=()
status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c at+cpin?)`
    for i in ${status[@]};
    do
        sts+=($i)
    done
    result=${sts[4]}
#    echo "$result"
    unset sts
if [ "$result" != "$isOK" ]
then
	echo "Something is wrong with SIM"
	exit 0
fi



${SUDO} $PATH_UTILS/get-cdc-wdm-num.sh -i $INTERFACE


path="$PATH_TEMP_DIR/temp"
wds_path="$path/temp-wds_$INTERFACE"
wds_ip_path="$path/temp-ip_$INTERFACE"
wds_ip_filter="$path/temp-ip-setting_$INTERFACE"
wdm=`(head -1 $PATH_TEMP_DIR/temp/$INTERFACE)`
mux="1"
apn="internet"

if [ -f $wds_path ];
then
    echo "not to dial twice!"
	exit 1
fi




echo -n ""  | ${SUDO} tee $wds_path
echo -n ""  | ${SUDO} tee $wds_ip_path
echo -n ""  | ${SUDO} tee $wds_ip_filter

echo 'Y' | ${SUDO} tee /sys/class/net/${INTERFACE}/qmi/raw_ip > /dev/null 2>&1 

${SUDO} qmicli -p -d $wdm --client-no-release-cid --wds-noop | ${SUDO} tee  $wds_path
while [ ! -s "$wds_path" ]
do
	echo "re-allocate the wds resource"
	sleep 0.5
	${SUDO} qmicli -p -d $wdm --client-no-release-cid --wds-noop | ${SUDO} tee  $wds_path
done
echo "Allocate wds resource succcess"
wds_id=`(cat $wds_path | grep CID | awk '{print $2}' | sed 's/.$//' | sed 's/^.//')`

${SUDO} qmicli -d $wdm --device-open-proxy --wds-start-network="ip-type=4,apn=$apn" --client-cid=$wds_id --client-no-release-cid
sleep 0.1
${SUDO} qmicli -p -d $wdm --wds-get-current-settings --client-cid=$wds_id --client-no-release-cid | ${SUDO} tee  $wds_ip_path > /dev/null 2>&1


${SUDO} $PATH_UTILS/read-setting.py $wds_ip_path $wds_ip_filter
sleep 0.2

ip=`(cat $wds_ip_filter | head -1)`
mask=`(cat $wds_ip_filter | head -2 | tail -1)`

${SUDO} ifconfig $INTERFACE up
${SUDO} ifconfig $INTERFACE $ip netmask $mask

if [ "$DGW" != "" ]
then
	DGW=`(cat $wds_ip_filter | tail -2 | head -1)`
	${SUDO} ip route del default > /dev/null 2>&1
	${SUDO} ip route append default via "$DGW" dev $INTERFACE  > /dev/null 2>&1
	${SUDO} udhcpc -f -n -q -t 5 -i $INTERFACE
else
	DGW=`(cat $wds_ip_filter | tail -2 | head -1)`
	${SUDO} ip route append default via "$DGW" dev $INTERFACE  > /dev/null 2>&1
fi
#udhcpc -f -n -q -t 5 -i wwan0

# Check if it is successful dial, If not, run disconnection and dial again
#ping test
if [ "$CHECK" == "do_check" ];
then
	PING_TEST $INTERFACE
	if [ $? != 0 ]; 
	then
		$PATH_UTILS/disconnect-qmi.sh -i $INTERFACE
		$PATH_UTILS/dial-qmi.sh -i $INTERFACE
	fi
fi

