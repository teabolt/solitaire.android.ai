#!/bin/bash

# clean up the live data directory
rm -f data/live/touchpoints_check
rm -f data/live/gameshot_check

# run two scripts in parallel
python3 src/detector.py & ~/Android/Sdk/tools/bin/./monkeyrunner src/android_io.py
