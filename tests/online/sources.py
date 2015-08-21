import os
import sys
sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.pardir,
            os.path.pardir
            ))
from online.sources import FileSource
from Queue import Queue
import threading
import logging
import time


class DummyPublisher(object):
    def __init__(self):
        self.queue = Queue()

class TestFileSource(object):
    def test_data_acquisition(self):
        logging.basicConfig(level=logging.DEBUG)
        p = DummyPublisher()
        e = threading.Event()
        filesource = FileSource(p, 4000, 'emg_data', abort=e)
        print 'Start filesource'
        filesource.start()
        for i in range(10):
            print 'Elements in Queue: {}'.format(p.queue.qsize())
            time.sleep(1)

        print 'Setting event'
        e.set()
        print 'Waiting until thread terminates'

if __name__ == '__main__':
    TestFileSource().test_data_acquisition()
