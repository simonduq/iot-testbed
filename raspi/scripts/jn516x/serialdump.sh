#!/bin/bash

log_path=$1
tty_path=`ls /dev/serial/by-id/*NXP_JN516?_USB_Dongle*`
if [ $? -ne 0 ]; then
   # No dongle present. Try DK4 development board
   tty_path=`ls /dev/serial/by-id/*NXP_DK4_Controller_Board*`
fi 
nohup ~/scripts/jn516x/contiki-serialdump -b1000000 $tty_path | ~/scripts/jn516x/contiki-timestamp > $log_path & > /dev/null 2> /dev/null
sleep 1
ps | grep "$! "
exit $?
