""" This module contains a cDAQ datasource for real-time emg. The source was
    separated to the others to use functionality independent of cDAQ libraries
"""
import PyDAQmx as pydaq
from threading import Thread
from threading import currentThread
from Queue import Queue
import json
import cPickle
import time
from online.messageclasses import ArrayMessage
import sys
import os
sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.pardir,
            os.path.pardir
        ))
import emg.data
import logging
from sources import AbstractSource


class CdaqSource(AbstractSource):
    """ Reads data from National Instrumnet compact Data Acquisition Chassie

        Attributes:
            channels (List): List of strings specifying channel to grab data
                from. Format of channel is <modulename>/ai<channel>.
            task_handle (pydaq.TaskHandle): Handle for data retieval task
            read (pycdaq.int32): Some sort of Flag?

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
        self._task_handle = pycdaq.TaskHandle()
        self._read = pycdaq.int32()

    def _setup_channels(self):
        """ Setup channels to be channels measuring voltage """
        for channel in self._channels:
            pydaq.DAQmxCreateAIVoltageChan(
                    self._task_handle,
                    channel,    # Channel, <channel_name>/ai<channel_num> e.g. emg/ai0
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
                )

    def acquire_data(self):
        num_samples = int(ArrayMessage.duration * self.samplingrate)
        try:
            data = numpy.zeros(
                (samplingrate, len(self._channels)),
                dtype=numpy.float64
                )
            pydaq.DAQmxCreateTask('', byref(self._task_handle))
            self._setup_channels()
            self._setup_sampling()
            pydaq.DAQmxStartTask(self._task_handle)

            while True:
                pydaq.DAQmxReadAnalogF64(
                        self._task_handle,
                        num_samples,
                        10.0,
                        pydaq.DAQmx_Val_GroupByChannel,
                        data,
                        data.size,
                        byref(self._read),
                        None
                        )
                yield data
        except pydaq.DAQError as err:
            logging.error('PyCDAQmx error in CdaqSource. Error was {}'.format(
                str(err)))
        except Exception as err:
            logging.error('Unexpected error occured in CdaqSource. Error ' + \
                    'was {}'.format(str(err)))
        finally:
            if self._abort is not None:
                self._abort.set()


