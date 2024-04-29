#!/bin/bash

SUDO=sudo


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

cd "$v3k_test_dir"
${SUDO} cp v3000_TMetro.sh /usr/local/bin
${SUDO} cp v3000_TMetro.service /etc/systemd/system
${SUDO} systemctl enable v3000_TMetro.service

