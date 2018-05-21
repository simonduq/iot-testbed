#!/usr/bin/env python3

import os
import shutil
import yaml
import subprocess
from IPython import embed
from os.path import expanduser

TASKS_PER_EXECUTION = 3
ALLOW_REPEAT = False

PATH_CONTIKI_NG = expanduser("~")+"/contiki-ng"
PATH_GITHUBIO = expanduser("~")+"/simonduq.github.io"
PATH_TASKLIST = expanduser("~")+"/cng-bot/tasklist.yml"
PATH_LASTRUN = expanduser("~")+"/cng-bot/last_run"

# Example tasklist.yml:
#- setup: test-csma
#  duration: 120
#- setup: test-tsch
#  duration: 120
#- setup: test-tsch-optims
#  duration: 120
#- setup: other
#  duration: 120
#  label: A custom run
#  repository: simonduq/contiki-ng
#  branch: wip/testbed
#  xppath: examples/benchmarks/rpl-req-resp
#  flags:
#    CONFIG: CONFIG_CSMA

def run(task):
    setupData = next(yaml.load_all(open(os.path.join(PATH_GITHUBIO, "_setups", task["setup"]+".md"), "r")))
    setupData.update(task)
    setup = task["setup"]
    repository = setupData["repository"]
    branch = setupData["branch"]
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
    os.system("make TARGET=zoul BOARD=firefly-reva %s clean node" %(flagsStr))
    #os.system("sudo docker run --mount type=bind,source=%s,destination=/home/user/contiki-ng -ti simonduq/contiki-ng bash -c 'make -C %s TARGET=zoul BOARD=firefly-reva %s clean node'" %(PATH_CONTIKI_NG, setupData["xppath"], flagsStr))
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
        # Create testbed job
        os.system("testbed.py create --platform zoul --copy-from %s --duration=%u"%(setup, setupData["duration"]))
        # Clean up
        os.system("git checkout develop\n")
        os.system("git reset --hard\n")
        os.system("git clean -fd\n")

def main():
    # save original working dir
    owd = os.getcwd()
    # read task list
    taskList = yaml.load(open(PATH_TASKLIST, "r"))

    if os.path.exists(PATH_LASTRUN):
        lastrun = int(open(PATH_LASTRUN, "r").read().rstrip())
    else:
        lastrun = -1

    runCount = TASKS_PER_EXECUTION if ALLOW_REPEAT else min(TASKS_PER_EXECUTION, len(taskList))

    for i in range(runCount):
        index = (lastrun + 1 + i) % len(taskList)
        run(taskList[index])
        os.chdir(owd)
        with open(PATH_LASTRUN, 'w') as f:
            f.write("%u\n"%(index))

main()
