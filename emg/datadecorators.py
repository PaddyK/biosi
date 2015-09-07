""" This module contains classes implementing the decorator pattern. Purpose
    is to easily streamline different operations on data.

    For more information on the decorator pattern refer to
    `Wikipedia <https://en.wikipedia.org/wiki/Decorator_pattern>`_

    All decorators manipulating data expect lists/generators of 2D-Numpy arrays,
    where the first dimension is the time.
"""

import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.join(
    os.path.realpath(__file__),
    os.path.pardir
    )))
from model.model import DataHoldingElement
from model.model import DataContainer

class AbstractDataDecorator(DataHoldingElement):
    """ Abstract base class for all concrete decorators
    """

    def __init__(self, data_holding_element, as_iterator):
        """ Initializes object
            Args:
                data_holding_element (model.model.DataHoldingElement): Any
                    instance whose class inhertis from
                    model.model.DataHoldingElement or provides same functions
                    and return values as defined in this class.

                as_iterator (boolean): If true object acts like an interator

            Note:
                If argument ``as_iterator`` is set to true, elements are worked
                on sequentially. One trial is processed at a time and returned,
                then the next one and so on.
                If ``as_iterator`` is set to false, all requested data is returned
                immediatly.
        """
        super(AbstractDataDecorator, self).__init__()
        self._element = data_holding_element
        self._is_iterator = as_iterator

    def _iterate(self):
        pass

    def _return(self):
        pass


class SamplingDecorator(AbstractDataDecorator):
    def calculate_factor(self, recording):
        """ Calculates samling factor

            Args:
                recording (model.model.Recording): Recording for which data
                    stored by ``self.element`` should be downsampled to
        """
        sr = recording.modality.frequency

    def _downsample(self, f_from, f_to, container):
        """ Samples signal down by taking the mean

            Args:
                f_from (int): Sampling-Rate of the data decorator gets from
                    its ``DataHoldingElement``
                f_to (int): Sampling-Rate data from ``DataHoldingElement``
                    should be brought to
                container (model.model.DataContainer): Container holding data
                    to decorate

            Raises:
                AssertionError if ``f_from`` is not a multiple from ``f_to``
        """
        factor, remainder = divmod(f_from, f_to)
        assert remainder == 0, 'SamplingDecorator._downsample cannot ' + \
                'sample signals to same frequencies. Frequency of the two ' + \
                'signals are not multiple of each other'
        return np.mean(np.reshape(-1, factor, contaner.data.shape[1]), axis=1)

    def _upsample(self, f_from, f_to, container):
        """ Samples signal up by repeating elements

            Args:
                f_from (int): Sampling-Rate of the data decorator gets from
                    its ``DataHoldingElement``
                f_to (int): Sampling-Rate data from ``DataHoldingElement``
                    should be brought to
                container (model.model.DataContainer): Container holding data
                    to decorate

            Raises:
                AssertionError if ``f_to`` is not a multiple from ``f_from``
        """
        factor, remainder = divmod(f_to, f_from)
        assert remainder == 0, 'SamplingDecorator._upsample: SamplingRates are ' + \
            'note multiple of each other. SamplingRates were {} and {}'.format(
                    f_to, f_from)
        return np.repeat(container.data, factor, axis=0)

    def _iterate(self, data_list):
        """ Loop over data and adapt it. Yield result.

            Args:
                data_list (Iterable): List or ``_iterate`` method of another
                    decorator

            Yields:
                container
        """
        for container in data_list:
            factor, rest = divmod(self.element.frequency, frequency)
            if factor == 0:
                contaner.data = self._upsample(
                        self.element.frequency,
                        frequency,
                        container
                        )
            else:
                container.data = self._downsample(
                        self.element.frequency,
                        factor,
                        remainder
                        )
            yield container

    def _return(self, data_list):
        """ Loop over all data in ``data_list`` and return result as list.

            Args:
                data_list (iterable): List or ``_iterate`` method of another
                    decorator

            Returns:
                List of containers
        """
        for container in data_list:
            factor, rest = divmod(self.element.frequency, frequency)
            if factor == 0:
                contaner.data = self._upsample(
                        self.element.frequency,
                        frequency,
                        container
                        )
            else:
                container.data = self._downsample(
                        self.element.frequency,
                        factor,
                        remainder
                        )
        return data_list

    def get_data(frequency, **kwargs):
        """ Sample data up or down depending on the frequency passed to this
            function.

            If attribute ``_is_iterator`` is set a function ``_iterate`` is
            returned as iterator, else list of model.model.DataContainer
            is returned.

            Args:
                frequency (int): Target frequency data should be brought to

            Raises:
                TypeError if frequency is not int
        """
        if type(frequency) is not int:
            raise TypeError('SamplingDecorator.get_data expects ' + \
                    '``frequency`` to be integer, {} given instead'.format(
                        type(frequency)
                        )
                    )
        data_list = self._element.get_data(*kwargs)

        if self._is_iterator:
            return self._iterate(data_list)
        else:
            return self._return(data_list)


class WindowDecorator(AbstractDataDecorator):
    def _calc_num_windows(self, timesteps, windowsize, stride):
        """ Based on duration of data element, windowsize and stride
            calculates number of windows.

            Args:
                timesteps (int): Number of timesteps (samples) of data
                windowsize (int): Size of window in timesteps
                stride (int): Size of stride in timesteps

            Returns:
                int
        """
        windows, remainder = divmod(timesteps - windowsize, stride)
        return windows

    def _expand_time(self, time, frequency):
        """ Calculates index from time in seconds and returns it

            Args:
                time (float): Time in seconds
                frequency (int): Sampling Rate of signal

            Returns:
                int
        """
        tmp = time * frequency
        point = int(tmp)
        if tmp - point != 0:
            warnings.warn('Time {} did not result in integer index for ' + \
                    'frequency {} in emg.datadecorators.WindowDecorator' + \
                    '._expand_time'
                    )
        return point

    def _iterate(self, windowsize, stride, datalist):
        """ Returns one window at a time

            Args:
                windowsize (float): Duration of window in seconds
                stride (float): Time difference between beginning of windows
                    in seconds
                datalist (iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Yields:
                model.model.DataContainer
        """
        for container in datalist:
            data = container.data
            counter = 0
            start = stride * num
            stop = windowsize + start

            while stop <= container.duration:
                yield container[start:stop]
                start = stride * num
                stop = windowsize + start

    def _return(self, windowsize, stride, datalist):
        """ Returns one window at a time

            Args:
                windowsize (float): Duration of window in seconds
                stride (float): Time difference between beginning of windows
                    in seconds
                datalist (iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Returns:
                List of model.model.DataContainer
        """
        result = []
        for container in datalist:
            data = container.data
            counter = 0
            start = stride * num
            stop = windowsize + start

            while stop <= container.duration:
                result.append(container[start:stop])
                start = stride * num
                stop = windowsize + start
        return result

    def get_data(windowsize, stride, **kwargs):
        """ Windowfies data. Returns them as list of iterator depending on
            attribute ``is_iterator``

            Args:
                windowsize (float): Size of windows in seconds
                stride (float): Difference between the beginning of two
                    consecutive windows in seconds
                kwargs (Dictionary): arguments for other methods

            Note:
                If ``windowsize * frequency`` results not in a natural number,
                value will be truncated. The same goes for stride.

            Returns:
                Iterator or List
        """
        dataelement = self._element.get_data(*kwargs)

        if self._is_iterator:
            return self._iterate(windowsize, stride, dataelement)
        else:
            return self._return(windowsize, stride, dataelement)


class RmsDecorator(AbstractDataDecorator):
    def _rms(self, windowsize, container):
        """ Applies Root-Mean-Square filter to data

            Args:
                windowsize (int): Size of window in samples
                container (model.model.DataContainer): Container holding data
                    to filter

            Raises:
                AssertionError if windowsize is not an Integer of windowsize
                larger than number of samples in container

            Returns:
                numpy.ndarray
        """
        values = container.data
        sum_of_squares = np.sum(np.square(values[:windowsize]), axis=1)
        filtered = np.sqrt(sum_of_squares)

        for i in range(windowsize, values.shape[0]):
            # To make filtering more performant, subtract first element of
            # previous windows from sum and add next value.
            # This corresponds to sliding the window one sample but does not
            # require to calculate the bulk of the window again, since it stays
            # the same.
            sum_of_squares = np.subtract(
                    sum_of_squares,
                    np.square(values[i - windowsize, :])
                    )
            sum_of_squares = np.add(sum_of_squares, np.square(values[i, :]))
            filtered = np.row_stack((filtered, np.sqrt(sum_of_squares)))
        return filtered

    def _iterate(self, windowsize, datalist):
        """ Yields data containers whose data has been filtered

            Args:
                windowsize (float): Size of windows in seconds
                datalist (iterable): Yielding model.model.DataContainer

            Yields:
                model.model.DataContainer
        """
        for container in datalist:
            filtered = self._rms(int(windowsize * container.frequency), container)
            container.data = filtered
            yield container

    def _return(self, windowsize, datalist):
        """ Returns List of data containers whose data has been filtered

            Args:
                windowsize (float): Size of windows in seconds
                datalist (iterable): Yielding model.model.DataContainer

            Returns:
                List of model.model.DataContainer
        """
        for container in datalist:
            filtered = self._rms(int(windowsize * container.frequency), container)
            container.data = filtered
        return datalist

    def get_data(self, windowsize, **kwargs):
        """ Returns iterator or list of model.model.DataContainer depending
            on attribute ``is_iterator``.

            Args:
                windowsize (float): Size of window for filtering in seconds.

            Note:
                You will use ``windowsize * sampling rate`` datapoints when
                applying RMS. So choose ``windowsize`` with care.

            Returns:
                List of iterator of model.model.DataContainer
        """
        datalist = self._element.get_data(*kwargs)

        if self._is_iterator:
            return self._iterate(windowsize, datalist)
        else:
            return self._iterate(windowsize, datalist)
        pass


class ArrayDecorator(AbstractDataDecorator):
    """ Represents end point of decorator stack and returns a 3D Array.
        Using iterator Decorator is pointless with this endpoint, since all
        DataContainer will be used to create the array.
    """
    def __init__(self, iterator):
        """ Initializes object
        """
        super(ArrayDecorator, self).__init__(self, iterator, False)

    def _iterate(self):
        raise NotImplementedError('Method _iterate not implemented ' + \
                'for ArrayDecorator')

    def _return(self, datalist):
        """ Creates 3d array and returns it

            Args:
                datalist (Iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Returns:
                np.ndarray
        """
        array = None
        for container in datalist:
            if array is None:
                array = container.data[np.newaxis, :, :]
            else:
                array = np.concatenate(
                        (array, contaner.data[np.newaxis, :, :]),
                        axis=0
                        )
        return array

    def get_data(self, **kwargs):
        """ Returns 3D array where first axis is number of trials, second
            axis is time and third dimension is number of channels

            Note:
                Data stored in DataContainer needs to have the same first
                dimension (same duration).
                This can be achieved using either ``PadzeroDecorator`` or
                ``WindowDecorator``.

            Returns:
                np.ndarray
        """
        datalist = self._element.get_data()
        return self._return(datalist)


class PadzeroDecorator(AbstractDataDecorator):
    """ Paddes data with zeros s.t. they all have the same length i.e. same
        duration.
        For this, all DataContainers have to be known. Therefore it does
        not make sense to use this decorator in context of iterable
        decorators.
    """
    def __init__(self, data_holding_element, up_front=False):
        super(AbstractDataDecorator, super).__init__(data_holding_element, False)
        self.up_front = front

    def _iterate(self):
        raise NotImplementedError('Function ``iterate`` not implemented for ' + \
                'class PadzeroDecorator')

    def _return(self, datalist, max_length):
        """ Returns list with padded DataContainer.

            Args:
                datalist (List): List containing model.model.DataContainer
                max_length (int): Maximal length (duration) of data (in samples)

            Returns:
                List
        """
        for container in datalist:
            to_pad = max_length - container.samples
            if to_pad == 0:
                continue
            if self.up_front:
                contaner.data = np.concatenate(
                        (container.data, np.zeros((to_pad, container.num_channels))),
                        axis=0
                        )
            else:
                contaner.data = np.concatenate(
                        axis=0,
                        (container.data, np.zeros((to_pad, container.num_channels)))
                        )
        return datalist

    def get_data(self, **kwargs):
        """ Returns List with padded arrays. If given data holding element is
            of type iterator, all elements will be polled.
        """
        datalist = self._element.get_data(*kwargs)
        max_dur = 0

        if type(datalist) == generator:
            tmp = [container for container in datalist]
            datalist = tmp

        for container in datalist:
            if container.samples > max_dur:
                max_dur = container.samples

        return self._return(datalist, max_dur)

