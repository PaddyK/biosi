""" This package contains message classes ro encode messages in nanomsg
    and send them over the wire
"""
import numpy as np
import time
import struct
import logging
logging.basicConfig(level=logging.DEBUG)


class ArrayMessage(object):
    """ Represents an array that is going to be send over the wire
    """
    header_format = '<Qfii'
    """ The format of the header appended before the actual data.
        See https://docs.python.org/3/library/struct.html for more information.
        During unpacking this attribute is used to separate data from auxialiary
        information
    """
    duration = 0.15
    """ Duration the array represented by this message is representing
    """
    def __init__(self, data, timestamp=None, sr=None):
        """ Initializes object
        
            Args:
                data (numpy.ndarray): Data for Message
                timestamp (long): Timestamp data was created in ms
                sr (int): Sampling-rate of data

            Note:
                If ``timestamp`` is not given, time when message is
                created is used
        """
        self._logger = logging.getLogger('ArrayMessageLogger')
        self._data = data
        self._samplingrate = None
        if timestamp is None:
            self._timestamp = int(time.time() * 1000)
        else:
            self._timestamp = timestamp
        if sr is not None:
            self._samplingrate = sr

    @property
    def data(self):
        """ Getter property for data attribute

            Returns:
                numpy.ndarray
        """
        return self._data

    @property
    def timestamp(self):
        """ Getter property for attribute timestamp

            Returns:
                localtime
        """
        return self._timestamp

    @classmethod
    def get_headerlength(self):
        """ Gets the length of the header based on attribute *header_format*

            Returns:
                int
        """
        return struct.calcsize(self.header_format)

    def serialize(self, sr):
        """ Returns a serialized representation of this object

            Args:
                sr (int): sampling rate with which data for message was sampled
            Returns:
                serialized object
        """
        header = struct.pack(
                self.header_format,
                self.timestamp,
                self.duration,
                sr,
                self.data.shape[0]
                )
        message = header + self.data.tostring()
        return message

    @classmethod
    def deserialize(cls, message):
        """ Initializes object from a message
        """
        logger = logging.getLogger('ArrayMessageLogger')
        headerlength = cls.get_headerlength()
        header = message[:headerlength]
        strdata = message[headerlength:]
        timestamp, duration, sr, nrows = struct.unpack(cls.header_format, header)

        try:
            data = np.fromstring(strdata, dtype='float64').reshape(nrows, -1)
        except Exception as e:
            logger.error('Unexpected error while deserializing array. Error was: ' + \
                    '{}'.format(e.message))
            raise e
        obj = cls(data, timestamp, sr)
        obj.duration = duration
        return obj

