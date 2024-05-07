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

mailhandle()
{
    # "$2" == "0" add log only
    # "$2" == "1" add log and send mail simultaneously
    
    if [ "$1" == "1" ]; then
	error_content="Loss connection"
    elif [ "$1" == "2" ]; then
	error_content="Flight mode toggling fail"
    elif [ "$1" == "3" ]; then
        error_content="GPIO toggling fail"
    elif [ "$1" == "4" ]; then
        error_content="SIM error"
    elif [ "$1" == "5" ]; then
        error_content="Thermal alarm"
    else
	error_content="Re-dial fail"
    fi

    echo "[LOG]"
    echo "time,`(date +%Y-%m-%d_%H-%M-%S)`" | sudo tee -a $TOP/temp/warning_log.txt  > /dev/null
    echo -e "$INTERFACE,$error_content\n" | sudo tee -a $TOP/temp/warning_log.txt > /dev/null
    
    if [ "$2" == "1" ]; then
	echo "[MAIL]"
	echo -e "time,`(date +%Y-%m-%d_%H-%M-%S)`\n$INTERFACE $error_content\n" | sudo tee $TOP/temp/mail_warning_log.txt > /dev/null
	$PATH_UTILS/v3k_test/check_temperature.sh | sudo tee -a $TOP/temp/mail_warning_log.txt > /dev/null
	
    	sudo python3 $PATH_UTILS/v3k_test/default-route-change-utility.py $INTERFACE
    	sudo python3 $PATH_UTILS/v3k_test/mail.py $INTERFACE $1 $TOP/temp/mail_warning_log.txt
    fi
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

# init counter
ping_fail_counter=0
flight_mode_counter=0
reset_counter=0
SIM_check_counter=0

#--------------check if warning log exists------------ 
if [ ! -f $TOP/temp/warning_log.txt ]; then
    sudo touch $TOP/temp/warning_log.txt
fi
#----------end of check if warning log exists---------

#--------------ping loop start-----------------
while true; do
    
    ping -W 1 -I $INTERFACE -c 1 8.8.8.8 > /dev/null

    if [ $? -eq 0 ]; then
        echo "[re-dial]: Ping successful - $(date)"
        ping_fail_counter=0
    else
        echo "[re-dial]: Ping failed - $(date)"
        ((ping_fail_counter++))
	 mailhandle "1" "0" # loss connection but add log only
    fi

    # ping out per 10s, ping fail > 30s, parameter can be modify
    if [ $ping_fail_counter -ge 2 ]; then
	ping_fail_counter=0
        echo "[re-dial]: Network failure"
	mailhandle "1" "1" # loss connection alarm
		        
	#-----------toggle flight mode--------------
	while [ $flight_mode_counter -lt 2 ]; do
		toggle_flight_mode "$INTERFACE"
		toggle_status=$?
		
		if [ "$toggle_status" == "0" ]; then
    			echo "[re-dial]: toggle flight mode success"
			echo "[re-dial]: waiting for flight mode on..."
			((flight_mode_counter=0))
			break
		else
    			echo "[re-dial]: toggle flight mode failed"
			((flight_mode_counter++))
			 mailhandle "2" "0" # flight mode toggle error but add log only
		fi
	done
	#---------end of toggle flight mode-----------
	
	sudo rm -rf "$TOP/temp/temp-wds_$INTERFACE"	
	sleep 5

	#--------------reset module---------------
        if [ $flight_mode_counter -ge 2 ]; then
		mailhandle "2" "1" # flight mode toggle error alarm
				
		while [ $reset_counter -lt 2 ]; do
			echo "[re-dial]: start resetting module"
                	ATCMD_filter "at+cfun=1,1" "1"
                	reset_status=$?

                	if [ "$reset_status" == "0" ]; then
                        	((reset_counter=0))
				echo "[re-dial]: waiting for module reset for 20s..."
			        sleep 20
                        	break
                	else
                        	echo "[re-dial]: reset mode failed"
                        	((reset_counter++))
                	fi
        	done

        fi
        #------------end of reset module----------

	#------------------toggle GPIO------------------------
	if [ $reset_counter -ge 2 ]; then
		echo "[re-dial]: start reading CPU temperature"
		$PATH_UTILS/v3k_test/check_temperature.sh
		CPU_temperature_status=$?
		if [ "$CPU_temperature_status" != "0" ]; then
			echo "[re-dial]: CPU temperature is too high"
			# log has been written in check_temperature.sh
			mailhandle "5" "1" # Thermal alarm
			exit 1
		else
			echo "[re-dial]: CPU temperature is normal"
			echo "[re-dial]: waiting for module power off at the most 30 sec..."
			$PATH_UTILS/v3k_test/v3000_power_off_5g_slot.sh -i $INTERFACE
			echo "[re-dial]: module power off completed"
			echo "[re-dial]: waiting for module power on"
			$PATH_UTILS/v3k_test/v3000_power_on_5g_slot.sh -i $INTERFACE
			echo "[re-dial]: module power on completed"
			
			mailhandle "3" "0" # GPIO toggle error but add log only
		fi

	fi
	#--------------end of toggle GPIO-----------------------
	
	$PATH_UTILS/check_quectel_exist.sh -i $INTERFACE

	#-------SIM check------------------
	echo "[re-dial]: start SIM check"
	ATCMD_filter "at+cfun?" "4"
	SIMcheck_status=$?

	if [ "$SIMcheck_status" != "0" ]; then
		((SIM_check_counter++))
		mailhandle "4" "0" # SIM check alarm but add log only
		
		if [ $SIM_check_counter -gt 2 ]; then
			mailhandle "4" "1" # SIM check alarm
	    		exit 1
    		fi
        else
		#--------------dial---------------
		echo "[re-dial]: start dialing"      	
		$PATH_UTILS/auto-connect-test.sh -i $INTERFACE
		if [ "$?" == "0" ]; then
			ping_fail_counter=0
			flight_mode_counter=0
			reset_counter=0
			SIM_check_counter=0
		else
			mailhandle "6" "1" # re-dial fail alarm
                        exit 1

		fi
		#-----------end of dial-----------         
        fi
	#----------end of SIM check-----------
    fi

    # pin out per 10s
    sleep 10
done
