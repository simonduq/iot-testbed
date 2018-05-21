#!/usr/bin/env python3

import re
import sys
import os
import fileinput
import math
import shutil
import yaml
import subprocess
import pandas as pd
from pandas import *
from datetime import *
from collections import OrderedDict
from IPython import embed
from os.path import expanduser

PATH_GITHUBIO = expanduser("~")+"/simonduq.github.io"

def main():
    if len(sys.argv) < 1:
        return
    else:
        dir = sys.argv[1].rstrip('/')
    date = open(os.path.join(dir, ".started"), 'r').readlines()[0].strip()
    duration = open(os.path.join(dir, "duration"), 'r').readlines()[0].strip()

    jobId = int(os.path.basename(dir).split("_")[0])

    taskData = yaml.load(open(os.path.join(dir, "task.yml"), "r"))

    # Generate .md file for the run
    githubPagesMdPath = os.path.join(PATH_GITHUBIO, "_runs", "%u.md"%(jobId))
    outFile = open(githubPagesMdPath, "w")
    outFile.write("---\n")
    outFile.write("date: %s\n" %(date))
    outFile.write("duration: %s\n" %(duration))

    outFile.write("setup: %s\n" %(taskData["setup"]))

    if "repository" in taskData:
        outFile.write("repository: %s\n" %(taskData["repository"]))
    if "branch" in taskData:
        outFile.write("branch: %s\n" %(taskData["branch"]))
    if "xppath" in taskData:
        outFile.write("path: %s\n" %(taskData["xppath"]))
    if "flags" in taskData:
        outFile.write("flags: %s\n" %(taskData["flags"]))

    outFile.write("commit: %s\n" %(taskData["commit"]))

    # Output relevant metrics
    ret = subprocess.check_output(["python3", os.path.join(dir, "parse.py"), dir])
    outFile.write(ret.decode("utf-8") )

    outFile.write("---\n")
    outFile.write("\n{% include run.md %}\n")

    # Copy logs to github parseEnergest
    githubPageLogPath = os.path.join(PATH_GITHUBIO, "_logs", "%u.txt"%(jobId))
    shutil.copyfile(os.path.join(dir, "logs", "log.txt"), githubPageLogPath)

    # Git ass new files
    os.chdir(PATH_GITHUBIO)
    os.system("git add %s" %(githubPagesMdPath))
    os.system("git add %s" %(githubPageLogPath))
    os.system("git commit -m 'Reuslts for job %u (%s)'" %(jobId, taskData["setup"]))

main()
