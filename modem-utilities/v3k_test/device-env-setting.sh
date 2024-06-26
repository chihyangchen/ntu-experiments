#!/bin/bash

SUDO=sudo
mail_receiver="'chihyang78@gmail.com','youngcy_chen@moxa.com'"

helpFunction()
{
    echo ""
    echo "Usage: $0 -d [Metro#xxx] "
    echo "ENTER 1, 2, 3 or 4"
    exit 1 # Exit script after printing help
}
while getopts "d:" opt
do
    case "$opt" in
        d ) DEV="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$DEV" ]
then
    echo "missing argument"
    helpFunction
fi
if [ "$DEV" == "1" ]
then
	GMAIL_PASS="niug---zcur---aqns---ndnl"
elif [ "$DEV" == "2" ]
then
	GMAIL_PASS="zwon---tdpy---gfhz---ndoc"
elif [ "$DEV" == "3" ]
then
	GMAIL_PASS="vbpu---vwcx---ynrw---iqch"
elif [ "$DEV" == "4" ]
then
	GMAIL_PASS="mjcr---xxtt---scuq---ljuv"
fi
cp mail.py.sample mail.py
to_be_replaced_pass="xxxx"
sed -i 's#'${to_be_replaced_pass}'#'${GMAIL_PASS}'#g' mail.py
sed -i 's/---/ /g' mail.py

to_be_replaced_receiver="who"
sed -i 's#'${to_be_replaced_receiver}'#'${mail_receiver}'#g' mail.py


v3k_test_dir=`(pwd)`
echo "$v3k_test_dir"

NAME="Metro#"
DEV="${NAME}${DEV}"
echo "$DEV"


cd ..
utility_dir=`(pwd)`
echo "$utility_dir"
to_be_replaced_dir="/home/moxa/young/ntu-experiments/modem-utilities"

sed -i 's#'${to_be_replaced_dir}'#'${utility_dir}'#g' PATH_for_NTU_exp


cd
home_dir=`(pwd)`
touch "${DEV}"

cd "$utility_dir"
${SUDO} cp PATH_for_NTU_exp /usr/local/bin

${SUDO} cp "$utility_dir/settings/70-persistent-net.rules" /etc/udev/rules.d/
${SUDO} udevadm control --reload-rules
${SUDO} udevadm trigger

source PATH_for_NTU_exp
CHECK_my_SATA_dir


cd "$v3k_test_dir"
${SUDO} cp v3000_TMetro.sh /usr/local/bin
${SUDO} cp v3000_TMetro.service /etc/systemd/system
${SUDO} systemctl enable v3000_TMetro.service

${SUDO} cp KEEP-re-dial.sh /usr/local/bin
#uncomment when ready to deploy
#
#${SUDO} cp v3000_TMetro_keepalive_1.service /etc/systemd/system
#${SUDO} cp v3000_TMetro_keepalive_2.service /etc/systemd/system
#${SUDO} systemctl enable v3000_TMetro_keepalive_1.service
#${SUDO} systemctl enable v3000_TMetro_keepalive_2.service
