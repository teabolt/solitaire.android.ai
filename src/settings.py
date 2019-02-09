#!/usr/bin/env python3
# Jython compatible

import os
import os.path


SCRIPT_PATH = os.path.realpath(__name__)
PROJECT_DIR = os.path.dirname(SCRIPT_PATH)

TRAINING_DATA_PATH = os.path.abspath(os.path.join(PROJECT_DIR, 'data/training'))
LIVE_DATA_PATH = os.path.abspath(os.path.join(PROJECT_DIR, 'data/live'))
if not os.path.isdir(LIVE_DATA_PATH):
    os.mkdir(LIVE_DATA_PATH)

TOUCHPOINTS_PATH = os.path.abspath(os.path.join(LIVE_DATA_PATH, 'touchpoints.dat'))
GAMESHOT_PATH = os.path.abspath(os.path.join(LIVE_DATA_PATH, 'gameshot.png'))
