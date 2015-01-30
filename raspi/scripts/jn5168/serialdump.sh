#!/bin/bash

#/home/user/testbed-tools/usb-hub-off.sh
#/home/user/testbed-tools/usb-hub-on.sh
log_path=$1
tty_path=`ls /dev/serial/by-id/*NXP_JN5168_USB_Dongle*`
nohup ~/scripts/jn5168/contiki-serialdump -b1000000 $tty_path | ~/scripts/jn5168/contiki-timestamp > $log_path & > /dev/null 2> /dev/null
sleep 1
ps | grep " $! "
exit $?
