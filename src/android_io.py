# jython 2.5.3

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage

import sys
# try:
#     import settings
# except ImportError:
#     sys.path.append('.')
#     import settings
import settings

import os
import os.path
import time
import datetime


PROPERTIES = [
    'build.board', 'build.brand', 'build.device',
    'display.width', 'display.height', 'display.density',
]


def init_device():
    device = MonkeyRunner.waitForConnection()
    print 'Connected to "%s"' % str(device)
    time.sleep(2)
    for prop in PROPERTIES:
        print prop + " is %s" % str(device.getProperty(prop))
    print('Initialisation complete, continuing ... press CTRL-C to stop at any time\n')
    time.sleep(1)
    return device


def current_time():
    curr = datetime.datetime.now()
    return curr.strftime('%Y_%m_%d_%H_%M_%S')


def take_screenshot(device, save_path=current_time, interactive=False):
    if interactive:
        raw_input('Press ENTER followed by CTRL-D to take a screenshot\n')
    screenshot = device.takeSnapshot()
    if save_path is current_time:
        path = os.path.join(settings.LIVE_DATA_PATH, '%s.png' % current_time())
    else:
        if not os.path.splitext(save_path)[1]:
            path = '%s.png' % os.splitext(save_path)[0]
        else:
            path = save_path
    print 'Saving at "%s"' % path
    screenshot.writeToFile(path, 'png')
    return screenshot


def read_touchpoints(path):
    touchpoints = []
    f = open(path, 'r')
    for line in f:
        x, y = map(int, line.split())
        touchpoints.append((x, y))
    f.close()
    return touchpoints


def touch(device, touchpoints, horizontal_drag_dist=0, vertical_drag_dist=100, drag_time=0.2, delay=0.5):
    for x, y in touchpoints:
        device.drag((x, y), (x+horizontal_drag_dist, y+vertical_drag_dist), drag_time)
        time.sleep(delay)


def main():
    print 'Starting Android Input-Output script ...'
    device = init_device()   # connect to the Android device (via USB cable)

    # begin 'write screenshot - read touchpoints' loop
    while True:
        screenshot = take_screenshot(device, save_path=settings.GAMESHOT_PATH, interactive=True)
        # make a gameshot check file to synchronise with the detector
        open(settings.GAMESHOT_CHECK_PATH, 'w').close()

        # live directory must not have previous check files
        # Poll for a 'check file' to read the touchpoint coordinates (block until coordinates are available)
        while not os.path.isfile(settings.TOUCHPOINTS_CHECK_PATH):
            time.sleep(1)
        # got a file, remove it to clean up for the next run
        os.remove(settings.TOUCHPOINTS_CHECK_PATH)

        path = settings.TOUCHPOINTS_PATH
        print 'Reading touchpoints from "%s"' % path
        touchpoints = read_touchpoints(path)
        print touchpoints

        print 'Acting on touchpoints (dragging cards down) ...'
        touch(device, touchpoints)
        print 'Acting on touchpoints quickly and diagonally ...'
        touch(device, touchpoints, horizontal_drag_dist=100, vertical_drag_dist=200, drag_time=0.00001, delay=0.2)
        print 'Done'
        print


if __name__ == '__main__':
    main()
