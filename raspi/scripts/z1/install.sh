#!/bin/bash

# Reboot the node
usb-hub-off.sh
usb-hub-on.sh
# Now program the node
ihex_path=$1
tty_path=`ls /dev/serial/by-id/*Zolertia_Z1*`
bsl_path=scripts/z1/z1-bsl-nopic
python $bsl_path --z1 -c $tty_path -e && sleep 2
python $bsl_path --z1 -c $tty_path -I -p $ihex_path && sleep 2
python $bsl_path --z1 -c $tty_path -r && sleep 1
