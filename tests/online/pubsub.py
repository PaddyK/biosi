import os
import sys
sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.pardir,
            os.path.pardir
            ))
from online.sources import FileSource
import online.publisher
import online.subscriber
from online.messageclasses import ArrayMessage
from Queue import Queue
import threading
import logging
import time

class TestPubSub(object):
    def setup_emg(self, url, e):
        publisher = online.publisher.EmgPublisher(url, abort=e)
        source = online.sources.FileSource(publisher, 4000, 'emg_data', abort=e)
        subscriber = online.subscriber.EmgSubscriber(url, abort=e)
        return source, publisher, subscriber

    def setup_kin(self, url, e):
        publisher = online.publisher.KinPublisher(url, abort=e)
        source = online.sources.FileSource(publisher, 4000, 'kin_data', abort=e)
        subscriber = online.subscriber.KinSubscriber(url, abort=e)
        return source, publisher, subscriber

    def test_communication(self, source, publisher, subscriber, e):
        print 'start source'
        source.start()
        print 'start publisher'
        publisher.start()
        print 'start subscriber'
        subscriber.start()

        count = 0
        for arrmsg in online.subscriber.array_iterator(ArrayMessage, subscriber):
            if count > 10:
                e.set()
                break
            print arrmsg.data.shape
            time.sleep(0.5)
            count += 1

    def test_emg_inproc(self):
        # Dereference returned tuple into positional arguments
        e = threading.Event()
        try:
            self.test_communication(*self.setup_emg('inproc://test'), e=e)
        except Exception as ex:
            e.set()
            raise ex

    def test_emg_tcp(self):
        e = threading.Event()
        try:
            self.test_communication(*self.setup_emg('tcp://192.168.0.16:5555'), e=e)
        except Exception as ex:
            e.set()
            raise ex

    def test_kin_inproc(self):
        e = threading.Event()
        # Dereference returned tuple into positional arguments
        try:
            self.test_communication(*self.setup_kin('inproc://test'), e=e)
        except Exception as ex:
            e.set()
            raise ex

    def test_kin_tcp(self):
        e = threading.Event()
        try:
            self.test_communication(*self.setup_kin('tcp://192.168.0.16:5555'), e=e)
        except Exception as ex:
            e.set()
            raise ex

    def test_together(self, urlemg, urlkin, e):
        emgsrc, emgpub, emgsub = self.setup_emg(urlemg, e)
        kinsrc, kinpub, kinsub = self.setup_kin(urlkin, e)

        print 'Start emg components'
        emgsrc.start()
        emgpub.start()
        emgsub.start()

        print 'Start kin components'
        kinsrc.start()
        kinpub.start()
        kinsub.start()

        for i in range(10):
            print 'fetch kin message'
            X_kin = online.subscriber.array_iterator(ArrayMessage, kinsub).next()
            print 'fetch emg message'
            X_emg = online.subscriber.array_iterator(ArrayMessage, emgsub).next()
            print 'Kin data: {}, EMG data: {}'.format(X_kin.data.shape, X_emg.data.shape)
            time.sleep(0.25)

        e.set()

    def test_together_tcp(self):
        e = threading.Event()
        try:
            self.test_together('tcp://192.168.0.16:5555', 'tcp://192.168.0.16:5556', e)
        except Exception as ex:
            e.set()
            raise ex

    def test_together_inproc(self):
        e = threading.Event()
        try:
            self.test_together('inproc://test_emg', 'inproc://test_kin', e)
        except Exception as ex:
            e.set()
            raise ex

