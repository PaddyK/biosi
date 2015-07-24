""" Module contains wrappers for different sources. Wrappers acquire data
    from respective source and make it available to distribute it using
    publisher from `publisher` module.
"""
import online
from threading import Thread
from Queue import Queue
import json

class AbstractSource(Thread):
    """ Abstract base class for sources
    """

    def __init__(self):
        """ Initializes object
        """
        self._queue = Queue()

    @property
    def queue(self):
        """ Getter property for queue attribute

            Returns:
                Queue.queue
        """
        return self._queue

    def acquire_data():
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

            self.queue.put(self.serialize(sample))

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
    import cPickle

    def __init__(self):
        super(AbstractSource, self).__init__()
        self._file = '../data/Proband_01.pkl'
        """ Path to pickled numpy ndarray
        """
        self._fh = None
        try:
            self._fh = cPickle.load(self._file)
        except Exception as e:
            print 'Error while opening file {}. Error was {}'.format(
                    self._file, e.message
                    )
            return

    def acquire_data():
        """ Reads data from a pickled numpy array
        """
        import time

        if sample.shape[0] <= 1:
            return None

        sample = self._fh[0, :]
        self._fh = self._fh[1:, :]
        time.sleep(0.001)
        return line


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
            raise NotImplementedError('Source for keyword {} not yet ' + \
                    'implemented'.format(source))
        elif source == 'kin':
            raise NotImplementedError('Source for keyword {} not yet ' + \
                    'implemented'.format(source))
        else:
            raise NotImplementedError('Unkown keyword {} enocuntered in ' + \
                    'SourceFactory.produce'.format(source)
                    )
