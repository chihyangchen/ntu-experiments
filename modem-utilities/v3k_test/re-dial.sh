#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/AT_CHECK
TOP=$PATH_TEMP_DIR
source $PATH_UTILS/quectel-path.sh
source $PATH_UTILS/AT_filter.sh
source $PATH_UTILS/toggle_flight_mode.sh

SUDO=sudo
AT_TIMEOUT=10000

CHECK_temp_dir

helpFunction()
{
    echo ""
    echo "Usage: $0 -i [INTERFACE]"
    echo "INTERFACE: network INTERFACE"
    exit 1 # Exit script after printing help
}

#------------check argument--------------
while getopts "i:t:" opt
do
    case "$opt" in
        i ) INTERFACE="$OPTARG" ;;
        t ) AT_TIMEOUT="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done
if [ -z "$INTERFACE" ]
then
    echo "missing argument"
    helpFunction
fi
#-----------end of check argument-------------

#-----------check device port----------------
LOCK_FILE=$TOP/temp/$INTERFACE.lock

while [ -f $LOCK_FILE ];
do

        echo "device port is occupied!"
        sleep 0.5
done
#------------end of check device port---------

#echo $INTERFACE

# 初始化连续失败次数
ping_fail_counter=0
flight_mode_counter=0
reset_counter=0
SIM_check_counter=0

echo $(date)

#--------------ping loop start-----------
while true; do
    # 执行 ping 命令并输出结果到/dev/null，不显示在终端上
    ping -W 1 -I $INTERFACE -c 1 8.8.8.8 > /dev/null

    # 检查 ping 命令的退出状态，如果成功则打印消息，否则打印失败消息
    if [ $? -eq 0 ]; then
        echo "Ping successful - $(date)"
        # 重置连续失败次数
        ping_fail_counter=0
    else
        echo "Ping failed - $(date)"
        # 连续失败次数加1
        ((ping_fail_counter++))
    fi

    # 如果连续失败次数超过3次（即连续超过30秒），则打印"network failure"并退出脚本
    if [ $ping_fail_counter -ge 1 ]; then
	ping_fail_counter=0
        echo "Network failure"
        
	#-----------toggle flight mode--------------
	while [ $flight_mode_counter -lt 2 ]; do
		toggle_flight_mode "$INTERFACE"
		toggle_status=$?
		
		if [ "$toggle_status" == "0" ]; then
    			echo "toggle_flight_mode success"
			((flight_mode_counter=0))
			break
		else
    			echo "toggle_flight_mode failed"
			((flight_mode_counter++))
		fi
	done
	#---------end of toggle flight mode-----------
	
	echo "waiting for flight mode on..."
	sleep 5

	#--------------reset module---------------
        echo "start resetting module"
	if [ $flight_mode_counter -ge 2 ]; then
		while [ $reset_counter -lt 2 ]; do
                	ATCMD_filter "at+cfun=1,1" "1"
                	reset_status=$?

                	if [ "$reset_status" == "0" ]; then
                        	echo "reset module success"
                        	((reset_counter=0))
                        	break
                	else
                        	echo "reset mode failed, start reading CPU temperature"
                        	((reset_counter++))
                	fi
        	done

        fi
        #------------end of reset module----------

	#------------------toggle GPIO------------------------
	if [ $reset_counter -ge 2 ]; then
		#read CPU temperature
		$PATH_UTILS/v3k_test/check_temperature.sh
		CPU_temperature_status=$?
		echo "temp=$?"
		if [ "$CPU_temperature_status" != "0" ]; then
			 exit 1 # add log & alarm
		else
			echo "waiting for module power off at the most 30 sec..."
			$PATH_UTILS/v3k_test/v3000_power_off_5g_slot.sh -i $INTERFACE
			echo "module power off completed"
			echo "waiting for module power on"
			$PATH_UTILS/v3k_test/v3000_power_on_5g_slot.sh -i $INTERFACE
			echo "module power on completed"
		fi

	fi
	#--------------end of toggle GPIO-------------------------

	echo "waiting for module reset..."
	sleep 20
	$PATH_UTILS/check_quectel_exist.sh -i $INTERFACE

	#-------SIM check------------------
	echo "start SIM check"
	ATCMD_filter "at+cpin?" "4"
	SIMcheck_status=$?

	if [ "$SIMcheck_status" != "0" ]; then
		((SIM_check_counter++))

		if [ $SIM_check_counter -gt 2 ]; then
        		exit 1 # add log & alarm
    		fi
        else
		#--------------dial---------------
        	${SUDO} rm -rf $PATH_TEMP_DIR/temp/temp*$INTERFACE
        	$PATH_UTILS/dial-qmi.sh -i $INTERFACE
		#-----------end of dial-----------         
        fi
	#----------end of SIM check-----------
    fi

    # 等待 10 秒pin
    sleep 10
done
