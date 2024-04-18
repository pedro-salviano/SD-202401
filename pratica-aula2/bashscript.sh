#!/bin/bash

MAX=80
STOP=0
while [ $STOP -eq 0 ]
do
    CPU="$(top -b -n1 | grep "Cpu(s)" | awk '{print $2 + $4}')"

    if [ "$(bc -l <<< "${CPU} < ${MAX}")" -eq 1 ]
    then
        python3 request_client.py &
    fi
    if [ "$(bc -l <<< "${CPU} > ${MAX}")" -eq 1 ]
    then 
        STOP=2
    fi
done
