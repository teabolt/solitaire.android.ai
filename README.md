# solitaire.android.ai

A project to demonstrate automatic user-like interaction between an Android phone and a local developer PC. The PC receives screenshots of the Android phone screen, and the Android phone receives touch events from the PC.

This interaction is applied to the card game Solitaire, that is an app on the Android phone. Screenshots are taken of the game and the game's cards are moved.

The ultimate goal is to completely automate the game so that cards are automatically moved to places where they should be. However, the project has not achieved this so far.

## Video demonstration
(TODO)

## Requirements
* Android Phone and a micro-USB cable that connects the phone to the PC
* Android SDK with the `monkeyrunner` tool (`~/Android/Sdk/tools/bin/monkeyrunner`) (based on Jython 2.5.3)
* Python 3 (CPython)
  * OpenCV 4.0 for Python 3

## Usage

### On Linux / Mac OS X
1. Execute the `run.sh` bash script
2. Press enter and CTRL+D to take a screenshot
3. Press any key when an OpenCV image window is active to close the image window and move on

### On Windows
(TODO)
1. At the same time execute both `android_io.py` and `detector.py`
    * `.../monkeyrunner android_io.py` (where `...` represents the directory where monkeyrunner is placed)
    * `py -3 detector.py`

## Implementation
* `monkeyrunner`, a tool of the Android SDK for testing and controlling an Android device, is used to take screenshots of the state of the game (current cards), and to send touch events to locations where certain objects in the game are present (open playing cards).
 * The screenshots are saved as 'png' file.
* `opencv`, a third-party library computer vision library, is used to locate and classify the cards in a screenshot image (the 'gameshot') and write the coordinates to where the cards are ('touchpoints').
  * The project contains all the possible card images with associated labels in ```data/training/```.
  * A difference is taken between the detected card and each of the training cards to recognise the card.
  * The touchpoints file ```touchpoints.dat``` is a newline-separated collection of coordinates (x and y components separated by a space).
* The processes are synchronised via polling and writing of 'indicator files'
  * The detector blocks until a screenshot is available. The Android IO code blocks until coordinates to touch are available.
  * Other solutions that did not work (interprocess communication based)
    * Using the ```signal``` module to send Unix signals between two processes, interrupt-based programming (problem - sending a signal kills the process)
    * Using the ```subprocess``` module to have a parent (controller) and a child (controlled) process and pipes for two-way communication (problem - pipes override stdin/stdout, but the user interacts with the processes via stdin/stdout).
    * Using ```multiprocessing``` with synchronisation, eg: locks (problem - the two Python programs are incompatible - CPython vs Jython, version 3 vs version 2).
  * Other solutions that could have been tried
    * sockets

## To-do / future enhancements
* Update 'run.sh' script to work well with paths / current working directory changes.
* Implement a 'run' script for Windows (.bat file).
* Make the detector show original images (not the preprocessed versions).
* Make the image recognition accurate and actually working in most cases by using contours of the suit/rank symbols in the training and live/test data
* Make a better 'settings' file (not .py but .json, .cfg, etc).
* Implement better process synchronisation, eg: signal interrupts, sockets, process pipes, etc.
* Solve the Solitaire game automatically by moving the cards and detecting changes from the screenshots *(original idea)

## Disclaimer
For educational purposes only. The Solitaire Android app belongs to its respective owners 'Solitaire Card Games , Inc.' and can be found at ('https://play.google.com/store/apps/details?id=com.lemongame.klondike.solitaire').
