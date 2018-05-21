#!/bin/bash

# Now program the node
bin_path=$1
bsl_address_path=$2
bsl_address=`cat $bsl_address_path`
tty_path=`ls /dev/serial/by-id/*Zolertia_Firefly*`
bsl_path=scripts/zoul/cc2538-bsl.py
python $bsl_path -e -w -v -a $bsl_address -p $tty_path $bin_path
sleep 1
# Reboot the node
usb-hub-off.sh
usb-hub-on.sh
sleep 2
