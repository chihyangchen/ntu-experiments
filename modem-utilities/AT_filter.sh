#!/bin/bash

source PATH_for_NTU_exp
source $PATH_UTILS/AT_CHECK
TOP=$PATH_TEMP_DIR
source $PATH_UTILS/quectel-path.sh
#echo $PATH_UTILS
SUDO=sudo
AT_TIMEOUT=10000

CHECK_temp_dir



function ATCMD_filter()
{
        sts=()
	cmd=$1
	index=$2

	status=`(${SUDO} $PATH_UTILS/qc-at.sh -i $INTERFACE -c $cmd)`
	#status=`(${SUDO} mxat -d $DEV_AT_PATH -c $cmd -t $AT_TIMEOUT)`
        for i in ${status[@]};
        do
                sts+=($i)
        done

    res=${sts[$2]}
    echo "$cmd $res"
    unset sts
        if [ "$res" != "$isOK" ]
        then
        echo "Something is wrong with SIM"
        return 1
        fi

        return 0
}

