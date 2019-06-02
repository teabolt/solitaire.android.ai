# solitaire.android.ai

Programmatically send drag gestures to an Android device, moving objects that appear on its UI, using screenshots as a guide.

This has been applied to the card game 'Solitaire' (on an existing app), where the program recognises and moves each of the cards that appear on-screen.

The goal is to automate the game itself, using this "IO interface".


## How does it work

<a href="https://developer.android.com/studio/test/monkeyrunner/">Monkeyrunner</a> is a Jython based tool in the Android SDK for automated tests. I use this tool in my program to retrieve device information, take screenshots, and send gestures.

On the "backend" side, there is a script, based on OpenCV, that processes the screenshots to recognise and find locations of playing cards.


## Requirements
* Connection between an Android device and *a local developer machine*.
  * i.e. A micro-USB can be used.
  * This does not work on its own.
* Android SDK with the <a href="https://developer.android.com/studio/test/monkeyrunner/">monkeyrunner</a> test automation tool. 
  * On Linux this can be found at (`~/Android/Sdk/tools/bin/monkeyrunner`)
* Python 3 (preferably CPython), with the following packages:
  * OpenCV
  * Numpy


## Usage

### Execute the platform-independet `run.py` script

```
git clone https://github.com/teabolt/solitaire.android.ai
cd solitaire.android.ai
python3 run.py
```

1. Wait for the device to initialise.
2. Press ENTER and CTRL+D to take a screenshot.
3. Press any key when an OpenCV image window is active to close the window and move on.
4. Press CTRL+C to quit at any time

You may want to configure `settings.py` if there are problems with paths.
If `run.py` does not work, try to manually and concurrently execute `android_io.py` and `detector.py`.

You will find that the `live` directory is created / modified as the program runs.


## Video demonstration (tested on Python 3.7.3, Ubuntu 18.04 LTS)
(TODO)


## Implementation Notes
* `settings.py`
  * paths of various files and directories used by the program.
* `run.py`
  * program entry point, sets up directories/files, executes `android_io.py` and `detector.py` as subprocesses.
  * uses the `subprocess` module.
* `src/android_io.py`
  * Jython 2.5.3 script
* `src/detector.py`
  * CPython 3 script
* `src/sync.py`
  * CPython and Jython compatible script for shared synchronisation functions.
* `src/game_strings.py`
  * Card strings such as rank, suit, and colour names.
* `data`
  * `training`
* `live`
  * `gameshot.png`
    * Screenshot of the game.
    * See `examples/` directory for how the files should look like.
  * `touchpoints.dat`
  * sync
    * empty files

Terminology:
* gameshot - a screenshot of the Solitaire card game.
* touchpoint - a coordinate pair that identifies where a card is on the Android device screen.

## FIXME

* `opencv`, a third-party computer vision library, used to locate and classify the cards in a screenshot image (the 'gameshot') and write the coordinates to where the cards are ('touchpoints').
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
* `live`
* `data/training`
* proc sync


A big problem was to integrate two differing Python implementations (CPython and Jython) that are on different versions (3.x and 2.x).


Image detection.


## List of Future Enhancements
* Solve the Solitaire game automatically by moving the cards and detecting changes from the screenshots.
* Implement better process synchronisation, i.e.: use signal interrupts, sockets, subprocess pipes, etc.
* Detect partially visible cards, not just those that are fully visible.
* Create a 'run.sh' script for Linux and 'run.bat' script for Windows.
* Better UI, i.e. when quitting with CTRL+C, user can see a bunch of errors
* ```detector.py``` at parts is a mess that needs refactoring


## Known issues
* Values for device screen dimensions and game object (cards, layout areas) are hard-coded.
* Stopping the script / stdout
* Broken monkeyrunner output
* Questionable detection accuracy (may want to use suit/rank symbols (contours) instead of comparison)


## Disclaimer
For educational purposes only. The Solitaire Android app belongs to its respective owners 'Solitaire Card Games , Inc.' and can be found at ('https://play.google.com/store/apps/details?id=com.lemongame.klondike.solitaire'). I do NOT own this app.