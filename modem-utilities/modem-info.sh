#!/bin/sh

PORT=$1
#while true 
#do
mxat -d $PORT -c at+qeng=\"servingcell\" -t 3000
mxat -d $PORT -c at+qeng=\"neighbourcell\" -t 3000
#done

