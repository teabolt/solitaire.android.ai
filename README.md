# solitaire.android.ai

Programmatically send gestures to an Android device, moving objects that appear on-screen, using screenshots as a guide.

This has been applied to the card game 'Solitaire' (an existing app), where the program recognises and moves the cards that appear in-game.


## How does it work

The program consists of two parts:

A <a href="https://developer.android.com/studio/test/monkeyrunner/">Monkeyrunner</a> based script that can get device information, take screenshots, and send drag gestures.

An <a href="https://opencv.org/">OpenCV</a>-based Python script that processes screenshots to recognise playing cards.


## Requirements

* Connection between an Android device and *a local developer machine*.
  * i.e. A micro-USB can be used.
  * This program does not work on its own.
* Android SDK with the <a href="https://developer.android.com/studio/test/monkeyrunner/">monkeyrunner</a> test automation tool. 
  * On Linux this can usually be found at (`~/Android/Sdk/tools/bin/monkeyrunner`)
* Python 3 (preferably CPython), with the following third-party packages:
  * OpenCV
  * Numpy


## Usage

```
git clone https://github.com/teabolt/solitaire.android.ai
cd solitaire.android.ai
python3 run.py
```

1. Wait for the connection to the device to initialise.
2. Press ENTER and CTRL+D to take a screenshot.
3. Press any key when an OpenCV window is active to close the window and move on.
4. Press CTRL+C to quit at any time.

You may want to configure `settings.py` if there are problems with paths.
If `run.py` does not work, try to execute `android_io.py` and `detector.py` at the same time manually.

You will find that the `live` directory is created and modified as the program runs.


## Video Demonstration (tested on Python 3.7.3, Ubuntu 18.04 LTS, Samsung Galaxy S7)

(TODO)


## Implementation Notes

### Project Structure
* `settings.py`
  * paths of various files and directories used by the program.
* `run.py`
  * program entry point, sets up directories/files, executes `android_io.py` and `detector.py` as subprocesses.
  * uses the `subprocess` module to run scripts concurrently.
* `src/android_io.py`
  * Jython 2.5.3 script (an implementation of Python that runs as Java).
  * Uses `com.android.monkeyrunner`, an automated testing tool in the Android SDK.
  * Connects to a device, takes screenshots, and sends drag gestures.
* `src/detector.py`
  * CPython 3 script.
  * Uses `opencv`, a computer vision library, for image processing.
  * Can locate (find coordinates of) and classify (tell suit and rank) the cards in a screenshot image (the 'gameshot') and write the coordinates of where the cards are ('touchpoints').
  * This is the 'AI' part, implemented with simple image manipulation and matching.
  * Localisation is achieved by finding the contours of the image, and checking the contour area against expected card area. Particularly, the game screen is divided into sections - the 'tableaux' (columns of cards from A to 2), 'foundation' (reverse of tableaux, four decks for each colour), and 'stock' (face-down cards) - and different image processing is applied depending on the section.
  * Classification (multi-label) is achieved by comparing (computing the difference between) an unknown card and all the cards in `data/training`, taking the most similar card as the class. *There are accuracy problems with this approach*.
  * Credits go to many online sources with code examples and ideas for the above.
* `src/sync.py`
  * CPython and Jython compatible script for shared synchronisation functions `do_signal` and `receive_signal` with clean up actions.
  * Based on file existence polling.
  * The 'detector' blocks until a screenshot is made, and 'android_io' blocks until touchpoints are written.
* `src/game_strings.py`
  * Card strings such as rank, suit, and colour names.
* `data`
  * `training`
    * Images of all the 52 cards in the standard deck.
    * Files have the format `suit_rank.png`.
* `live`
  * `gameshot.png`
    * A screenshot of the game.
    * See `examples/` directory for how the files should look like.
  * `touchpoints.dat`
    * A list of touchpoints (coordinate pairs).
    * Each pair is on a line on its own (newline-separated).
    * Each pair's components are space-separated.
  * `.syncfile` files
    * Empty "indicator files" used to implement process synchronisation.

### Terminology
* gameshot - a screenshot of the Solitaire card game.
* touchpoint - a coordinate pair that identifies where a card is on an Android device screen.

### Misc
* A big problem was to integrate CPython 3 and Jython 2 - two different Python implementations, in two different versions. Common solutions did not work.
* Interprocess Communication (IPC) solutions:
  * `signal` module to send Unix signals between two processes, interrupt-based programming 
    * Problem: Sending such signals killed one of the processes.
  * `subprocess` module with a parent process (controller) and a child process (controlled), and pipes for two-way communication
    * Problem: Pipes overrode stdin/stdout, but the user interacts with the program through stdin/stdout.
  * `multiprocessing` module with synchronisation primitives, i.e.: locks 
      * The CPython and Jython scripts were incompatible.
  * sockets
    * This has not been tried yet, and looks like a good solution for running the two scripts on two different machines.


## List of Future Enhancements
* (Original goal) Solve the Solitaire game automatically by moving the cards and detecting changes from the screenshots.
* Use percentages (or some other relative measurement) instead of hard-coded values for screen dimensions, coordinates.
* Detect partially visible cards, not just those that are fully visible.
* For classifying cards, use suit/rank symbols (contouors) instead of the full card.
* Try using sockets for process synchronisation.
* Implement better, interrupt-driven (not polling-based as it is now) process synchronisation.
* Make a 'run.sh' script for Linux and 'run.bat' script for Windows.
* Create a better UI, i.e. currently, when quitting with CTRL+C, the user can see a bunch of errors.
* Refactor ```detector.py```.


## Known Issues
* *Hard-coded values* for device screen dimensions, game objects (cards, sections), preprocessing.
  * This program will likely not work on phones with different screen dimensions.
* Sometimes monkeyrunner fails to connect and garbled output is given.
  * A work-around is to kill the program and try again.
* Card classification accuracy is questionnable (often the card rank/suit is misclassified)
* Stopping the script does not always work (get weird output, need to send CTRL+C multiple times).


## Disclaimer
For educational purposes only. The Solitaire Android app used in this project and shown in the video belongs to its respective owners 'Solitaire Card Games , Inc.' and can be found at ('https://play.google.com/store/apps/details?id=com.lemongame.klondike.solitaire'). I do NOT own this app.