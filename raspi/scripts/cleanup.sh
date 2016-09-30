usb-hub-off.sh
rm logs/$1/log.txt -rf
rmdir -p logs/$1
rm tmp/* -rf
rmdir tmp
