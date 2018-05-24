#!/usr/bin/env python3

import re
import sys
import os
import fileinput
import math
import shutil
import yaml
import subprocess
import datetime
import pytz
import pandas as pd
from pandas import *
from collections import OrderedDict
from IPython import embed
from os.path import expanduser

PATH_GITHUBIO = expanduser("~")+"/simonduq.github.io"
PATH_JOBS = expanduser("~")+"/jobs"
PATH_HISTORY = expanduser("~")+"/cng-bot/history"

# get job directory from id
def get_job_directory(job_id):
  if os.path.isdir(PATH_JOBS):
    for f in os.listdir(PATH_JOBS):
      if f.startswith("%d_"%(job_id)):
        return os.path.join(PATH_JOBS, f)
  return None

def timestamp():
  return datetime.now(tz=pytz.timezone('Europe/Stockholm')).isoformat()

def log(msg):
    ts = timestamp()
    print(msg)
    with open(PATH_HISTORY, "a") as f:
        f.write("%s: %s\n" %(ts, msg))

def main():
    if len(sys.argv) < 2:
        print("Required parameter: jobId")
        return
    else:
        jobId = int(sys.argv[1].rstrip('/'))

    dir = get_job_directory(jobId)

    if dir == None:
        log("Job not found")
        return
    if not os.path.exists(os.path.join(dir, ".started")):
        log("Job never started")
        return
    if not os.path.exists(os.path.join(dir, ".stopped")):
        log("Job not stopped")
        return
    logFile = os.path.join(dir, "logs", "log.txt")
    if not os.path.exists(logFile):
        log("Log file not found")
        return

    log("Processing job %u (dir: %s)" %(jobId, dir))

    # Parse log file
    log("Parsing file %s" %(logFile))
    try:
        parsingRet = subprocess.check_output(["python3", os.path.join(dir, "parse.py"), logFile])
    except subprocess.CalledProcessError as e:
        log("Parsing failed. Aborting.")
        return

    date = open(os.path.join(dir, ".started"), 'r').readlines()[0].strip()
    duration = open(os.path.join(dir, "duration"), 'r').readlines()[0].strip()

    taskData = yaml.load(open(os.path.join(dir, "task.yml"), "r"))

    # Update github pages repository
    os.chdir(PATH_GITHUBIO)
    os.system("git pull origin master")

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
        outFile.write("xppath: %s\n" %(taskData["xppath"]))
    if "flags" in taskData:
        outFile.write("flags: %s\n" %(taskData["flags"]))

    outFile.write("commit: %s\n" %(taskData["commit"]))
    # Output result of log parsing
    outFile.write(parsingRet.decode("utf-8") )

    outFile.write("---\n")
    outFile.write("\n{% include run.md %}\n")
    outFile.flush()

    # Copy logs to github parseEnergest
    # Update github pages repository
    os.chdir(os.path.join(dir, "logs"))
    shutil.move("log.txt", "%u.txt"%(jobId))
    githubPageLogPath = os.path.join(PATH_GITHUBIO, "_logs", "%u.zip"%(jobId))
    os.system("zip %s %s" %(githubPageLogPath, "%u.txt" %(jobId)))

    # Git add new files and push
    # Update github pages repository
    os.chdir(PATH_GITHUBIO)
    os.system("git add %s" %(githubPagesMdPath))
    os.system("git add %s" %(githubPageLogPath))
    os.system("git commit -m 'Reuslts for job %u (%s)'" %(jobId, taskData["setup"]))
    os.system("git push origin master")

main()
