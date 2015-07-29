""" Module contains wrappers for different sources. Wrappers acquire data
    from respective source and make it available to distribute it using
    publisher from `publisher` module.
"""
import online
from threading import Thread
from Queue import Queue
import json
import cPickle
import time
from messageclasses import ArrayMessage

class AbstractSource(Thread):
    """ Abstract base class for sources
    """

    def __init__(self, publisher, samplingrate):
        """ Initializes object
        """
        super(AbstractSource, self).__init__()
        self._samplingrate = samplingrate
        self._publisher = publisher

    def acquire_data(self):
        pass

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
            self._publisher.queue.put(message.serialize(4000))

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
    """

    def __init__(self, publisher, samplingrate):
        super(FileSource, self).__init__(publisher, samplingrate)
        self._file = 'data/Proband_01.pkl'
        """ Path to pickled numpy ndarray
        """
        self._data = None
        try:
            with open(self._file, 'rb') as fh:
                self._data = cPickle.load(fh)
        except Exception as e:
            print 'Error while opening file {}. Error was {}'.format(
                    self._file, e.message
                    )
            return

    def acquire_data(self):
        """ Reads data from a pickled numpy array as list

            Returns:
                List
        """

        if self._data.shape[0] <= 1:
            return None

        arr = self._data[:ArrayMessage.duration * 4000]
        self._data = self._data[ArrayMessage.duration * 4000:]
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
