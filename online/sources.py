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
import PyDAQmx as pydaq
import numpy as np
logging.basicConfig(level=logging.DEBUG)

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
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)

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
        for sample in self.acquire_data():
            if sample is None:
                print 'No new data available - shutting down data source'
                if self._abort is not None:
                    self._abort.set()
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

            Yields:
                numpy.ndarray
        """
        start = 0
        num_samples = int(ArrayMessage.duration * self._samplingrate)
        stop = num_samples
        while stop < self._data.shape[0]:
            yield self._data[start:stop]
            start = stop
            stop = start + num_samples


class CdaqSource(AbstractSource):
    """ Reads data from National Instrumnet compact Data Acquisition Chassie

        Attributes:
            channels (List): List of strings specifying channel to grab data
                from. Format of channel is <modulename>/ai<channel>.
            task_handle (pydaq.TaskHandle): Handle for data retieval task
            read (pydaq.int32): Some sort of Flag?

        Example for channel:
            cDAQ module was named ``emg`` in _NI MAX_ program and electrode
            is added to channel one at emg, then channel description is
            emg/ai0
    """
    def __init__(self, publisher, samplingrate, modality, channels, abort=None):
        super(CdaqSource, self).__init__(
                publisher,
                samplingrate,
                'CdaqSource',
                abort=abort
                )
        self._channels = channels
        self._task_handle = pydaq.TaskHandle()
        self._read = pydaq.int32()

    def _setup_channels(self):
        """ Setup channels to be channels measuring voltage """
        channels = ','.join(self._channels)

        pydaq.DAQmxCreateAIVoltageChan(
                self._task_handle,
                channels,    # Channel, <channel_name>/ai<channel_num> e.g. emg/ai0
                '',
                pydaq.DAQmx_Val_RSE,
                -10.0,  # Max value
                10.0,   # Min Value
                pydaq.DAQmx_Val_Volts, # Unit to measure
                None
                )

    def _setup_sampling(self, num_samples):
        """ Setup how, then and often measurements hould be taken """
        pydaq.DAQmxCfgSampClkTiming(
                self._task_handle,
                '',
                self._samplingrate,
                    # Sampling rate at which cdaq looks for data. IMPORTANT
                    # this is NOT the same as the sampling rate of the EMG
                    # device (although it makes sense). EMG can sample at 1kHz
                    # and program can sample with only 10Hz
                pydaq.DAQmx_Val_Rising, # Flank of clock, here rising
                pydaq.DAQmx_Val_ContSamps,  # Continueous samples (also fixed
                num_samples                 # number possible)
                # num_samples must be over all channels (size of array)
                )

    def acquire_data(self):
        num_samples = int(ArrayMessage.duration * self._samplingrate)
        try:
            pydaq.DAQmxCreateTask('', pydaq.byref(self._task_handle))
            self._setup_channels()
            self._setup_sampling(data.size)
            pydaq.DAQmxStartTask(self._task_handle)

            while True:
                data = np.zeros(
                    (num_samples * len(self._channels)),
                    dtype=np.float64
                    )
                pydaq.DAQmxReadAnalogF64(
                        self._task_handle,
                        num_samples, # Numbe of samples to read per channel
                        10.0,   # Wait 10 seconds until timeout occurs
                        pydaq.DAQmx_Val_GroupByChannel,
                            # Group by channels interleaves samples of channels. So
                            # samples are stored : sample_channel1, sample_channel2,
                            # sample_channel_3, sample_channel1, ...
                        data,   # Array to read data into
                        data.size,
                        pydaq.byref(self._read), # Number of samples read for
                                                 # each channel
                        None
                        )
                yield data.reshape(-1, len(self._channels))
        except pydaq.DAQError as err:
            self._logger.error('PyCDAQmx error in CdaqSource. Error was {}'.format(
                str(err)))
        except Exception as err:
            self._logger.('Unexpected error occured in CdaqSource. Error ' + \
                    'was {}'.format(str(err)))
        finally:
            if self._abort is not None:
                self._abort.set()


class SourceFactory(object):
    """ Factory class producing a source
    """

    def produce(self, source, kwargs):
        """ Returns a source given an string

            Args:
                source (String): Identifier of data source

            Supported sources:
                file, cdaq, vicon 
        """
        if source == 'file':
            return FileSource(**kwargs)
        elif source == 'cdaq':
            return CdaqSource(**kwargs)
        elif source == 'vicon':
            msg = 'Source for keyword {} not yet implemented'.format(source)
            raise NotImplementedError(msg)
        else:
            msg = 'Unkown keyword {} enocuntered in SourceFactory.produce'.format(source)
            raise NotImplementedError(msg)
