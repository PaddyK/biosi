import os
import sys
sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.pardir,
            os.path.pardir
            ))
from online.sources import FileSource, CdaqSource
from online.messageclasses import ArrayMessage
from Queue import Queue
import threading
import logging
import time
import matplotlib.pyplot as plt
import numpy as np


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


class CdaqSourceTest(object):

    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('CdaqSourceTest')
        cls.logger.setLevel(logging.DEBUG)
        cls.queue = Queue()

    def test_data_acquisition(self):
        e = threading.Event()
        source = CdaqSource(self, 1000, 'emg', ['emg/ai0', 'emg/ai2'], abort=e)
        self.logger.info('Start Source')
        source.start()
        arr = None

        for i in range(10):
            msg = ArrayMessage.deserialize(self.queue.get())
            if arr is None:
                arr = msg.data
            else:
                arr = np.row_stack((arr, msg.data))
            self.logger.debug(msg.data.shape)
        self.logger.info('Stop testing')
        e.set()
        fig, axes = plt.subplots(2, 1, figsize=(32,12))
        axes[0].plot(arr[:, 0])
        axes[1].plot(arr[:, 1])
        plt.show()

if __name__ == '__main__':
    CdaqSourceTest.setup()
    test = CdaqSourceTest()
    test.test_data_acquisition()

