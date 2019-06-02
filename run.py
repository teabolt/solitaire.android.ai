#!/usr/bin/env python3
# cython

import os
import subprocess

import settings


# Clean up synchronisation files from previous runs, if any
try:
    os.remove(settings.TOUCHPOINTS_SYNCFILE_PATH)
except OSError:
    pass
try:
    os.remove(settings.GAMESHOT_SYNCFILE_PATH)
except OSError:
    pass


# Create the LIVE directory if needed
os.makedirs(settings.LIVE_DIR, exist_ok=True)


# Start execution
args = [settings.GAMESHOT_PATH, settings.TOUCHPOINTS_PATH, 
        settings.GAMESHOT_SYNCFILE_PATH, settings.TOUCHPOINTS_SYNCFILE_PATH]

# android io script in the background
p1 = subprocess.Popen([settings.JYTHON_INTERPRETER, settings.ANDROID_PATH, *args])

# detector script, wait for it to finish
p2 = subprocess.call([settings.CPYTHON_INTERPRETER, settings.DETECTOR_PATH, *args, settings.TRAINING_DATA_DIR]) 