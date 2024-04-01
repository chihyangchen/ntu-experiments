#!/bin/bash

# The value can only be defined in quectel=path.sh
source quectel-path.sh

GET_AT_PATH $1

if [ -e $DEV_AT_PATH ]; then
    echo "$1 module exists."
else
	echo "No related module"
fi

