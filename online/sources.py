""" Module contains wrappers for different sources. Wrappers acquire data
    from respective source and make it available to distribute it using
    publisher from `publisher` module.
"""
import online
from threading import Thread
from threading import currentThread
from Queue import Queue
import json
import cPickle
import time
from messageclasses import ArrayMessage
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(os.path.join(__file__, os.path.pardir))),
    'emg'
    ))
import emg.data
import logging

class AbstractSource(Thread):
    """ Abstract base class for sources
    """

    def __init__(self, publisher, samplingrate, name, abort=None):
        """ Initializes object

            Args:
                publisher (online.publisher.AbstractPublisher): Reference to
                    publisher thread object
                samplingrate (int): Sampling Rate of data provided by source
                name (String): Name of Thread
                abort (threading.Event, optional): Event signalling, that
                    Thread should shut down
        """
        super(AbstractSource, self).__init__(name=name)
        self._samplingrate = samplingrate
        self._publisher = publisher
        self._abort = abort

    def acquire_data(self):
        pass

    @property
    def samplingrate(self):
        """ Returns sampling rate of data provided by source

            Returns:
                int
        """
        return self._samplingrate

    def run(self):
        """ Starts Thread

            Runs as long as new data is available. If `acquire_data` returns
            `None` thread is terminated
        """
        while True:
            sample = self.acquire_data()
            if sample is None:
                print 'No new data available - shutting down data source'
                break
            message = ArrayMessage(sample)
            self._publisher.queue.put(message.serialize(self.samplingrate))

            if self._abort is not None:
                if self._abort.is_set():
                    self._cleanup()
                    logging.info('{} - Abort event set. Exiting...'.format(
                        currentThread().getName()
                        ))
                    break

    def _cleanup(self):
        """ Cleans up ressources when exiting
        """
        pass

    def serialize(self, sample):
        """ Serializes object to send it over the wire

            Args:
                sample (Object): Object to be serialized

            Returns:
                Serialized String
        """
        return json.dumps(sample)


class FileSource(AbstractSource):
    """ Reads data from a file and makes it available.

        currently from WAY-GAAL experiment thing a session
    """

    def __init__(self, publisher, samplingrate, modality, abort=None, name='FileSource'):
        super(FileSource, self).__init__(publisher, samplingrate, name, abort=abort)
        self._file = 'data/P1/HS_P1_S1.mat'
        """ Path to pickled numpy ndarray
        """
        self._data = None
        try:
            with open(self._file, 'rb') as fh:
                self._data = emg.data.read_session(self._file)[modality].values
        except Exception as e:
            print 'Error while opening file {}. Error was {}'.format(
                    self._file, e.message
                    )
            return

    def acquire_data(self):
        """ Reads data from a previously read numpy array

            Returns:
                numpy.ndarray
        """

        if self._data.shape[0] <= 1:
            return None

        arr = self._data[:int(ArrayMessage.duration * self._samplingrate)]
        self._data = self._data[int(ArrayMessage.duration * self._samplingrate):]
        time.sleep(ArrayMessage.duration)
        return arr


class SourceFactory(object):
    """ Factory class producing a source
    """

    def produce(self, source):
        """ Returns a source given an string

            Args:
                source (String): Identifier of data source

            Supported sources:
                file, emg, kin
        """
        if source == 'file':
            return FileSource()
        elif source == 'emg':
            msg = 'Source for keyword {} not yet implemented'.format(source)
            raise NotImplementedError(msg)
        elif source == 'kin':
            msg = 'Source for keyword {} not yet implemented'.format(source)
            raise NotImplementedError(msg)
        else:
            msg = 'Unkown keyword {} enocuntered in SourceFactory.produce'.format(source)
            raise NotImplementedError(msg)
