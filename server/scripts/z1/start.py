#!/usr/bin/env python

# Simon Duquennoy (simonduq@sics.se)

import sys
import os
import subprocess
import sys
sys.path.append('/usr/testbed/scripts')
from pssh import *

REMOTE_LOGS_PATH = "/home/user/logs"
REMOTE_SCRIPTS_PATH = "/home/user/scripts"
REMOTE_Z1_SCRIPTS_PATH = os.path.join(REMOTE_SCRIPTS_PATH, "z1")
REMOTE_TMP_PATH = "/home/user/tmp"
REMOTE_FIRMWARE_PATH = os.path.join(REMOTE_TMP_PATH, "firmware.ihex")

if __name__=="__main__":
  
  if len(sys.argv)<2:
    print "Job directory parameter not found!"
    sys.exit(1)
    
  # The only parameter contains the job directory
  job_dir = sys.argv[1]

  # Look for the firmware
  elf_path = None
  if os.path.isdir(job_dir):
   for f in os.listdir(job_dir):
    if f.endswith(".z1"):
      elf_path = os.path.join(job_dir, f)
      break
       
  if elf_path == None:
    print "No z1 firmware found!"
    sys.exit(2)
   
  ihex_path = elf_path[0:elf_path.rfind(".")]+".ihex"
  
  print "Generating ihex from %s to %s"%(elf_path, ihex_path)
  os.system("msp430-objcopy %s -O ihex %s" %(elf_path, ihex_path))
        
  hosts_path = os.path.join(job_dir, "hosts")
  # Copy firmware to the nodes
  if pscp(hosts_path, ihex_path, REMOTE_FIRMWARE_PATH, "Copying z1 firmware to the PI nodes") != 0:
    sys.exit(3)
  # Program the nodes
  if pssh(hosts_path, "%s %s"%(os.path.join(REMOTE_Z1_SCRIPTS_PATH, "install.sh"), REMOTE_FIRMWARE_PATH), "Installing z1 firmware") != 0:
    sys.exit(4)
  # Start serialdump
  remote_log_dir = os.path.join(REMOTE_LOGS_PATH, os.path.basename(job_dir), "log.txt")
  if pssh(hosts_path, "%s %s"%(os.path.join(REMOTE_Z1_SCRIPTS_PATH, "serialdump.sh"), remote_log_dir), "Starting serialdump") != 0:
    sys.exit(5)
