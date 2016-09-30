#!/bin/bash

log_path=$1
tty_path=`ls /dev/serial/by-id/*Zolertia_Firefly*` 
nohup ~/scripts/zoul/contiki-serialdump -b115200 $tty_path | ~/scripts/zoul/contiki-timestamp > $log_path & > /dev/null 2> /dev/null
sleep 1
ps | grep "$! "
exit $?
