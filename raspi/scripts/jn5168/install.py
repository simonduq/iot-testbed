#!/usr/bin/env python

# Simon Duquennoy (simonduq@sics.se)

import sys
import os
import subprocess
import time

if __name__=="__main__":
  
  if len(sys.argv)<2:
    print "Firmware parameter not found!"
    sys.exit(1)
    
  # The only parameter points to the firmware
  firmware_path = sys.argv[1]
       
  if not os.path.exists(firmware_path):
    print "Firmware not found!"
    sys.exit(2)
    
  # Locate ttyUSB file
  tty_path = None
  for f in os.listdir("/dev/serial/by-id"):
    if "NXP_JN5168_USB_Dongle" in f:
      tty_path = os.path.join("/dev/serial/by-id", f)
      break

  if tty_path == None:
    print "No JN5168 serial device found!"
    sys.exit(3)

  print "Installing jn5168 firmware %s, USB dev %s"%(firmware_path,tty_path)

  # We make a maxium of 5 attempts
  cnt = 0
  while cnt < 5:
    # First reset the node so it enters programming mode
    os.system("/home/user/testbed-tools/usb-hub-off.sh")
    os.system("/home/user/testbed-tools/usb-hub-on.sh")
    time.sleep(1)
    # Now actually program the node
    if subprocess.call(["/home/user/testbed-tools/JennicModuleProgrammer", "-V", "10", "-v", "-s", tty_path, "-I", "38400", "-P", "1000000", "-f", firmware_path]) == 0:
      # Reboot the node
      os.system("/home/user/testbed-tools/usb-hub-off.sh")
      os.system("/home/user/testbed-tools/usb-hub-on.sh")
      print "Success"
      sys.exit(0)
    else:
      cnt += 1

print "Failued after %d attempts"%(cnt)
sys.exit(4)
