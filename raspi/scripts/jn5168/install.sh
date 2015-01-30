#!/bin/bash
 
# First reset the node so it enters programming mode
sleep 1
usb-hub-off.sh
usb-hub-on.sh
sleep 1
# Now program the node
firmware_path=$1
tty_path=`ls /dev/serial/by-id/*NXP_JN5168_USB_Dongle*`
~/scripts/jn5168/JennicModuleProgrammer -V 10 -v -s $tty_path -I 38400 -P 1000000 -f $firmware_path
if [ $? -ne 0 ]; then
    exit 1
fi
sleep 1
# Reboot the node
usb-hub-off.sh
usb-hub-on.sh
sleep 3

