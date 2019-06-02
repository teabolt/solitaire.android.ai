# cpython and jython compatible

"""Temporary file and polling-based process synchronisation"""

import time
import os
import os.path


def do_signal(syncfile, msg):
    print(msg)
    open(syncfile, 'w').close()


def receive_signal(syncfile, msg):
    print(msg)
    while not os.path.isfile(syncfile):
        time.sleep(1)
    # got the file, remove it to clean up for the next run
    receive_cleanup(syncfile)


def receive_cleanup(syncfile):
    os.remove(syncfile)