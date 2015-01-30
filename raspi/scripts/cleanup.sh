usb-hub-off.sh
rm logs/$1/log.txt
rmdir -p logs/$1
rm tmp/*
rmdir tmp
