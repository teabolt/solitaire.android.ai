# jython 2.5.3


import sys
import os
import os.path
import time
import datetime

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage

from sync import do_signal, receive_signal


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
    print('Initialisation complete, continuing ... press CTRL+C to stop at any time\n')
    time.sleep(1)
    return device


def current_time():
    curr = datetime.datetime.now()
    return curr.strftime('%Y_%m_%d_%H_%M_%S')


def take_screenshot(device, save_path=current_time, interactive=False):
    if interactive:
        raw_input('Press ENTER followed by CTRL+D to take a screenshot (CTRL+C to stop)\n')
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


def touch(device, x, y, horizontal_drag_dist=0, vertical_drag_dist=100, drag_time=0.2, delay=0.5):
    device.drag((x, y), (x+horizontal_drag_dist, y+vertical_drag_dist), drag_time)
    time.sleep(delay)


def main():
    print '[%s] Starting Android Input-Output script ...' % os.path.basename(sys.argv[0])
    GAMESHOT_PATH, TOUCHPOINTS_PATH, GAMESHOT_SYNCFILE_PATH, TOUCHPOINTS_SYNCFILE_PATH = sys.argv[1:]
    device = init_device()   # connect to the Android device (via USB cable)

    # begin 'write screenshot - read touchpoints' loop
    while True:
        screenshot = take_screenshot(device, save_path=GAMESHOT_PATH, interactive=True)

        # make a gameshot check file to synchronise with the detector
        do_signal(GAMESHOT_SYNCFILE_PATH, 'Screenshot taken, signaling to detector')

        # Poll for a 'check file' to read the touchpoint coordinates (block until coordinates are available)
        receive_signal(TOUCHPOINTS_SYNCFILE_PATH, 'Waiting for detector to finish working with the image')

        print 'Reading touchpoints from "%s"' % TOUCHPOINTS_PATH
        touchpoints = read_touchpoints(TOUCHPOINTS_PATH)
        print touchpoints

        print 'Acting on touchpoints (dragging cards down) ...'
        for x, y in touchpoints:
            touch(device, x, y)
        print 'Acting on touchpoints (faster speed and diagonal) ...'
        for x, y in touchpoitns:
            touch(device, x, y, horizontal_drag_dist=100, 
                vertical_drag_dist=200, drag_time=0.00001, delay=0.2)
        print 'Done with this "screenshot-touch" iteration'
        print


if __name__ == '__main__':
    main()