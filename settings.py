# cpython and jython compatible

import os
import os.path
import sys


# OS PATHS
USER_DIR = os.path.expanduser('~')


# INTERPRETER PATHS
CPYTHON_INTERPRETER = 'python3'
JYTHON_INTERPRETER = os.path.join(USER_DIR, 'Android/Sdk/tools/bin/./monkeyrunner') # OVERRIDE ME IF NEEDED


# PROJECT PATHS
SCRIPT_PATH = os.path.abspath(sys.argv[0])
PROJECT_DIR = os.path.dirname(SCRIPT_PATH)


# PATHS TO SOURCE FILES
DETECTOR_PATH = os.path.join(PROJECT_DIR, 'src/detector.py')
ANDROID_PATH = os.path.join(PROJECT_DIR, 'src/android_io.py')


# PATHS TO DIRECTORIES WITH DATA
TRAINING_DATA_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'data/training'))
LIVE_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'live'))


# PATH TO DATA FILES CREATED DURING EXECUTION
TOUCHPOINTS_PATH = os.path.abspath(os.path.join(LIVE_DIR, 'touchpoints.dat'))
GAMESHOT_PATH = os.path.abspath(os.path.join(LIVE_DIR, 'gameshot.png'))


# PATHS TO PROCESS SYNCHRONISATION FILES CREATED DURING EXECUTION
TOUCHPOINTS_SYNCFILE_PATH = os.path.abspath(os.path.join(LIVE_DIR, 'touchpoints_check.syncfile'))
GAMESHOT_SYNCFILE_PATH = os.path.abspath(os.path.join(LIVE_DIR, 'gameshot_check.syncfile'))