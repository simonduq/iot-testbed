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
REMOTE_JN_SCRIPTS_PATH = os.path.join(REMOTE_SCRIPTS_PATH, "jn516x")
REMOTE_TMP_PATH = "/home/user/tmp"
REMOTE_NULL_FIRMWARE_PATH = os.path.join(REMOTE_JN_SCRIPTS_PATH, "null.jn516x.bin")

if __name__=="__main__":
  
  if len(sys.argv)<2:
    print "Job directory parameter not found!"
    sys.exit(1)
    
  # The only parameter contains the job directory
  job_dir = sys.argv[1]
       
  hosts_path = os.path.join(job_dir, "hosts")
  # Kill serialdump
  pssh(hosts_path, "killall contiki-serialdump -9", "Stopping serialdump")
  # Program the nodes with null firmware
  if pssh(hosts_path, "%s %s"%(os.path.join(REMOTE_JN_SCRIPTS_PATH, "install.sh"), REMOTE_NULL_FIRMWARE_PATH), "Uninstalling jn516x firmware") != 0:
    sys.exit(4)

