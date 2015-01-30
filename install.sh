cp -R server/scripts/* /usr/testbed/scripts/
parallel-rsync -h /usr/testbed/scripts/all-hosts -l user -azv --recursive raspi/scripts /home/user
