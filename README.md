# solitaire.android.ai

A project to demonstrate automatic user-like interaction between an Android phone and a local developer PC. The PC receives screenshots of the Android phone screen, and the Android phone receives touch events from the PC.

## Video demonstration

## Requirements
* Android Phone
* Micro-USB cable capable of connecting the phone to the PC
* Android SDK with monkeyrunner (`~/Android/Sdk/tools/bin/monkeyrunner`) (Jython-based)
* Python 3 (CPython)

## Usage

## Implementation

## To-do / future enhancements
* Update 'run.sh' script to work well with paths / current working directory changes.
* Implement a 'run' script for Windows (.bat file).
* Make the detector show original images (not the preprocessed versions).
* Make the image recognition accurate and actually working in most cases by using contours of the suit/rank symbols in the training and live/test data
* Make a better 'settings' file (not .py but .json, .cfg, etc).
* Implement better process synchronisation, eg: signal interrupts, sockets, process pipes, etc.
* Solve the Solitaire game automatically by moving the cards and detecting changes from the screenshots *(original idea)

## Disclaimer
For educational purposes only. The Solitaire Android app belongs to its respective owners.
