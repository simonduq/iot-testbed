#!/usr/bin/env python3

import os
import sys
import shutil
import yaml
import subprocess
import datetime
import pytz
from IPython import embed
from os.path import expanduser

TESTBED_PATH = "/usr/testbed"
LOCK_PATH = os.path.join(TESTBED_PATH, "lock")
PATH_CURR_JOB = os.path.join(TESTBED_PATH, "curr_job")
PATH_POST_PROCESSING = os.path.join(TESTBED_PATH, "scripts/contiki-ng-bot/cng-bot-parse-script.sh")

PATH_CONTIKI_NG = expanduser("~")+"/contiki-ng"
PATH_GITHUBIO = expanduser("~")+"/simonduq.github.io"
PATH_TASKLIST = expanduser("~")+"/cng-bot/tasklist.yml"
PATH_LASTRUN = expanduser("~")+"/cng-bot/last_run"
PATH_HISTORY = expanduser("~")+"/cng-bot/history"

# Example tasklist.yml:
#tasks-per-execution: 2
#allow-repeat: true
#tasks:
#  - setup: test-csma
#    duration: 120
#  - setup: test-tsch
#    duration: 120
#  - setup: test-tsch-optims
#    duration: 120
#  - setup: other
#    duration: 120
#    label: A custom run
#    repository: simonduq/contiki-ng
#    branch: wip/testbed
#    xppath: examples/benchmarks/rpl-req-resp
#    flags:
#      CONFIG: CONFIG_CSMA

def lock_is_taken():
    return os.path.exists(LOCK_PATH)

def lock_aquire():
    open(LOCK_PATH, 'a').close()

def lock_release():
    os.remove(LOCK_PATH)

def do_quit(status):
    lock_release()
    sys.exit(status)

def timestamp():
  return datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')).isoformat()

def log(msg):
    ts = timestamp()
    print(msg)
    with open(PATH_HISTORY, "a") as f:
        f.write("%s: %s\n" %(ts, msg))

def run(task):
    setupData = next(yaml.load_all(open(os.path.join(PATH_GITHUBIO, "_setups", task["setup"]+".md"), "r")))
    setupData.update(task)
    setup = task["setup"]
    repository = setupData["repository"]
    branch = setupData["branch"]
    log("Preparing")
    # Go to Contiki-NG
    os.chdir(PATH_CONTIKI_NG)
    # Add remote
    os.system("git remote add %s git@github.com:%s.git\n"%(repository, repository))
    # Fetch and check out branch
    os.system("git fetch %s %s\n"%(repository, branch))
    os.system("git checkout %s/%s\n"%(repository, branch))
    os.system("git reset --hard %s/%s\n"%(repository, branch))
    os.system("git clean -fd\n")
    # Get git commit hash
    task["commit"] = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode("utf-8")
    # Go to xp path
    os.chdir(setupData["xppath"])
    # Build
    flagsStr = " ".join(["%s=%s"%(x[0],x[1]) for x in setupData["flags"].items()]) if "flags" in setupData else ""
    log("Building")
    os.system("make TARGET=zoul BOARD=firefly-reva %s clean node" %(flagsStr))
    # Check if file was built
    if os.path.isfile("node.zoul"):
        # Create directory that contains the run data
        if not os.path.exists(setup):
            os.makedirs(setup)
        # Create YAML file with data about the task
        with open(os.path.join(setup, "task.yml"), 'w') as f:
            yaml.dump(task, f)
        # Copy parsing file
        shutil.copyfile("parse.py", os.path.join(setup, "parse.py"))
        # Copy firmware
        shutil.copyfile("node.zoul", os.path.join(setup, "node.zoul"))
        log("Scheduling")
        # Create testbed job
        os.system("testbed.py create --platform zoul --copy-from %s --duration=%u --post-processing=%s --nested"%(setup, setupData["duration"], PATH_POST_PROCESSING))
        # Clean up
        os.system("git checkout develop\n")
        os.system("git reset --hard\n")
        os.system("git clean -fd\n")

def main():
    # Take lock. Once we have it, we know no other job will be started
    if lock_is_taken():
        print("Lock is taken. Aborting.")
        sys.exit(1)
    else:
        lock_aquire()

    # If there is a jub running, abort
    if os.path.exists(PATH_CURR_JOB):
        # Not need to create file PATH_ABORTED; we did not have time
        # to create any job
        log("Job already running. Abort.")
        do_quit(1)
        return

    log("CNG bot starting.")
    # save original working dir
    owd = os.getcwd()
    # read task list
    taskConfig = yaml.load(open(PATH_TASKLIST, "r"))
    taskList = taskConfig["tasks"]

    if os.path.exists(PATH_LASTRUN):
        lastrun = int(open(PATH_LASTRUN, "r").read().rstrip())
    else:
        lastrun = -1

    runCount = taskConfig['tasks-per-execution'] if taskConfig['allow-repeat'] else min(taskConfig['tasks-per-execution'], len(taskList))

    for i in range(runCount):
        index = (lastrun + 1 + i) % len(taskList)
        log("Building and scheduling job %u" %(index))
        run(taskList[index])
        os.chdir(owd)
        with open(PATH_LASTRUN, 'w') as f:
            f.write("%u\n"%(index))

    # Start jobs
    log("Starting jobs.")
    os.system("testbed.py start --nested")

    do_quit(0)

main()
