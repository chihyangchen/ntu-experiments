#!/usr/bin/bash

# This script is to capture the location info from the GPS dongle

#interval=1
#FILE_PATH="sample"
FILE_PATH=`(date +%Y_%m%d_%H%M)`"_GPS_info"
: > $FILE_PATH


while true
do
	(gpspipe -uu -w) >> $FILE_PATH
#	sleep $interval
done

