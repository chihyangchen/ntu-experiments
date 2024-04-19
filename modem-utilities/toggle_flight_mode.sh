#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/AT_CHECK
TOP=$PATH_TEMP_DIR
source $PATH_UTILS/quectel-path.sh
source $PATH_UTILS/AT_filter.sh
#echo $PATH_UTILS
SUDO=sudo
AT_TIMEOUT=10000

CHECK_temp_dir

toggle_flight_mode()
{

	GET_AT_PATH $INTERFACE

	max_retry=1
	retry_cfun0=0
	retry_cfun1=0

	# 執行 at+cfun=0 命令
	ATCMD_filter "at+cfun=0" "1"
	CMD_status=$?
	#echo $CMD_status
	while [ "$CMD_status" != "0" ] && [ "$retry_cfun0" -lt "$max_retry" ]; do
		ATCMD_filter "at+cfun=0" "1"
		CMD_status=$?

		((retry_cfun0++))
	done
	
	# 執行 at+cfun=1 命令
	ATCMD_filter "at+cfun=1" "1"
	CMD_status=$?
	while [ "$CMD_status" != "0" ] && [ "$retry_cfun1" -lt "$max_retry" ]; do
     		ATCMD_filter "at+cfun=1" "1"
		CMD_status=$?

    		((retry_cfun1++))
	done
		
	${SUDO} rm -f ${LOCK_FILE}

	# 檢查最終 CMD_status 的值
	if [ "$CMD_status" != "0" ]; then
   		return 1 #fail
	else
    		return 0 #success
	fi

}

