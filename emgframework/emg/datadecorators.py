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
from online.messageclasses import ArrayMessage
import logging

class AbstractDataDecorator(DataHoldingElement):
    """ Abstract base class for all concrete decorators

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
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

    def get_data(self, kwargs):
        pass


class SamplingDecorator(AbstractDataDecorator):
    """ Samples data up or down.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
            frequency (int): Frequency to which data should be adopted
    """
    def __init__(self, frequency, data_holding_element, as_iterator=False):
        """ Initializes object.
            
            Args:
                frequency (int): Target frequency for data
                data_holding_element (DataHoldingElement): Data source
                as_iterator (bool): Whether to act as decorator
        """
        super(SamplingDecorator, self).__init__(data_holding_element, as_iterator)
        self._frequency = frequency

    def _downsample(self, container):
        """ Samples signal down by taking the mean

            Args:
                f_from (int): Sampling-Rate of the data decorator gets from
                    its ``DataHoldingElement``
                container (model.model.DataContainer): Container holding data
                    to decorate

            Raises:
                AssertionError if ``f_from`` is not a multiple from ``f_to``
        """
        factor, remainder = divmod(container.frequency, self._frequency)
        assert remainder == 0, 'SamplingDecorator._downsample cannot ' + \
                'sample signals to same frequencies. Frequency of the two ' + \
                'signals are not multiple of each other'
        ret = None
        rows, rest = divmod(container.shape[0], factor)
        if rest != 0:
            ret = np.mean(
                    container.data[:-rest].reshape(-1, factor, container.shape[1])
                    ,axis=1
                    )
        else:
            ret = np.mean(
                    container.data.reshape(-1, factor, container.shape[1]),
                    axis=1
                    )
        return ret

    def _upsample(self, container):
        """ Samples signal up by repeating elements

            Args:
                f_from (int): Sampling-Rate of the data decorator gets from
                    its ``DataHoldingElement``
                container (model.model.DataContainer): Container holding data
                    to decorate

            Raises:
                AssertionError if ``f_to`` is not a multiple from ``f_from``
        """
        factor, remainder = divmod(self._frequency, container.frequency)
        assert remainder == 0, 'SamplingDecorator._upsample: SamplingRates are ' + \
            'note multiple of each other. SamplingRates were {} and {}'.format(
                    self._frequency, f_from)
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
            factor, rest = divmod(container.frequency, self._frequency)
            if factor == 0:
                container.data = self._upsample(container)
            else:
                container.data = self._downsample(container)
            container.frequency = self._frequency
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
            factor, rest = divmod(container.frequency, self._frequency)
            if factor == 0:
                container.data = self._upsample(container)
            else:
                container.data = self._downsample(container)
            container.frequency = self._frequency
        return data_list

    def get_data(self, **kwargs):
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
        if type(self._frequency) is not int:
            raise TypeError('SamplingDecorator.get_data expects ' + \
                    '``frequency`` to be integer, {} given instead'.format(
                        type(self._frequency)
                        )
                    )
        data_list = self._element.get_data(**kwargs)

        if self._is_iterator:
            return self._iterate(data_list)
        else:
            return self._return(data_list)


class WindowDecorator(AbstractDataDecorator):
    """ Windowfies each trial.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
            windowsize (float): Duration of window in seconds
            stride (float): Time between consecutive windows in seconds
    """
    def __init__(self, windowsize, data_holding_element, stride=None, as_iterator=False):
        """
            Args:
                windowsize (float): Size of window in seconds
                data_holding_element (DataHoldingElement): Data source
                as_iterator (bool): Whether to act as decorator
                stride (float): Size of stride in seconds
        """
        super(WindowDecorator, self).__init__(data_holding_element, as_iterator)
        self._windowsize = windowsize
        self._stride = stride

    def _iterate(self, datalist):
        """ Returns one window at a time

            Args:
                datalist (iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Yields:
                model.model.DataContainer
        """
        # use_default_stride is used to determine whether to advance time window
        # bout only one time step.
        use_default_stride = False
        if self._stride is None:
            use_default_stride = True

        for container in datalist:
            if use_default_stride:
                self._stride = 1 / container.frequency
            data = container.data
            num = 0
            start = 0
            stop = self._windowsize

            while stop <= container.duration:
                yield container[start:stop]
                num += 1
                start = self._stride * num
                stop = self._windowsize + start

    def _return(self, datalist):
        """ Returns one window at a time

            Args:
                datalist (iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Returns:
                List of model.model.DataContainer
        """
        use_default_stride = False
        if self._stride is None:
            use_default_stride = True

        result = []
        for container in datalist:
            if use_default_stride:
                self._stride = 1 / container.frequency
            data = container.data
            num = 0
            start = 0
            stop = self._windowsize

            while stop <= container.duration:
                result.append(container[start:stop])
                num += 1
                start = self._stride * num
                stop = self._windowsize + start
        return result

    def get_data(self, **kwargs):
        """ Windowfies data. Returns them as list of iterator depending on
            attribute ``is_iterator``

            Args:
                kwargs (Dictionary): arguments for other methods

            Note:
                If ``windowsize * frequency`` results not in a natural number,
                value will be truncated. The same goes for stride.

            Returns:
                Iterator or List
        """
        dataelement = self._element.get_data(**kwargs)

        if self._is_iterator:
            return self._iterate(dataelement)
        else:
            return self._return(dataelement)


class RmsDecorator(AbstractDataDecorator):
    """ Performs Root-Mean-Square filtering.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
            windowsize (float): Duration of window in seconds
    """
    def __init__(self, windowsize, data_holding_element, as_iterator=False):
        """ Initializes object

            Args:
                data_holding_element (DataHoldingElement): Data source
                as_iterator (bool): Whether to act as decorator
                windowsize (float): Size of window for filtering in seconds.
        """
        super(RmsDecorator, self).__init__(data_holding_element, as_iterator)
        self._windowsize = windowsize

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
        sum_of_squares = np.square(values[:windowsize])
        filtered = np.sqrt(np.mean(sum_of_squares, axis=0))

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
            filtered = np.row_stack((
                filtered,
                np.sqrt(np.mean(sum_of_squares, axis=0))
            ))
        return filtered

    def _iterate(self, datalist):
        """ Yields data containers whose data has been filtered

            Args:
                datalist (iterable): Yielding model.model.DataContainer

            Yields:
                model.model.DataContainer
        """
        for container in datalist:
            filtered = self._rms(int(self._windowsize * container.frequency), container)
            container.data = filtered
            yield container

    def _return(self, datalist):
        """ Returns List of data containers whose data has been filtered

            Args:
                datalist (iterable): Yielding model.model.DataContainer

            Returns:
                List of model.model.DataContainer
        """
        for container in datalist:
            filtered = self._rms(int(self._windowsize * container.frequency), container)
            container.data = filtered
        return datalist

    def get_data(self, **kwargs):
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
        datalist = self._element.get_data(**kwargs)

        if self._is_iterator:
            return self._iterate(datalist)
        else:
            return self._return(datalist)
        pass


class ArrayDecorator3D(AbstractDataDecorator):
    """ Represents end point of decorator stack and returns a 3D Array.
        Using iterator Decorator is pointless with this endpoint, since all
        DataContainer will be used to create the array.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
    """
    def __init__(self, iterator):
        """ Initializes object

            Args:
                data_holding_element (DataHoldingElement): Data source
        """
        super(ArrayDecorator3D, self).__init__(iterator, False)

    def _iterate(self):
        """ Not implemented for this Class
        """
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
                        (array, container.data[np.newaxis, :, :]),
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
        datalist = self._element.get_data(**kwargs)
        return self._return(datalist)


class ArrayDecorator2D(AbstractDataDecorator):
    """ Represents end point of decorator stack and returns a 2D Array.
        Using iterator Decorator is pointless with this endpoint, since all
        DataContainer will be used to create the array.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.

    """
    def __init__(self, iterator):
        """ Initializes object

            Args:
                data_holding_element (DataHoldingElement): Data source
        """
        super(ArrayDecorator2D, self).__init__(iterator, False)

    def _iterate(self):
        """ Not implemented for this Class
        """
        raise NotImplementedError('Method _iterate not implemented ' + \
                'for ArrayDecorator')

    def _return(self, datalist):
        """ Creates 2d array and returns it

            Args:
                datalist (Iterable): Iterable yielding elements of type
                    model.model.DataContainer

            Returns:
                np.ndarray
        """
        array = None
        for container in datalist:
            if array is None:
                array = container.data
            else:
                array = np.row_stack((array, container.data))
        return array

    def get_data(self, **kwargs):
        """ Returns 2D array where first axis is number of trials, second
            axis is time and third dimension is number of channels

            Note:
                Data stored in DataContainer needs to have the same first
                dimension (same duration).
                This can be achieved using either ``PadzeroDecorator`` or
                ``WindowDecorator``.

            Returns:
                np.ndarray
        """
        datalist = self._element.get_data(**kwargs)
        return self._return(datalist)


class PadzeroDecorator(AbstractDataDecorator):
    """ Paddes data with zeros s.t. they all have the same length i.e. same
        duration.
        For this, all DataContainers have to be known. Therefore it does
        not make sense to use this decorator in context of iterable
        decorators.

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
            up_front (boolean): Whether to pad from front or back

    """
    def __init__(self, data_holding_element, up_front=False):
        """ Initializes object
            Args:
                data_holding_element (model.model.DataHoldingElement): Any
                    instance whose class inhertis from
                    model.model.DataHoldingElement or provides same functions
                    and return values as defined in this class.
                up_front (boolean): Whether to pad from front or back
        """
        super(PadzeroDecorator, self).__init__(data_holding_element, False)
        self.up_front = up_front

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
                container.data = np.concatenate(
                        (
                            np.zeros((to_pad, container.num_channels)),
                            container.data
                        ),
                        axis=0
                        )
            else:
                container.data = np.concatenate(
                        (
                            container.data,
                            np.zeros((to_pad, container.num_channels))
                        ),
                        axis=0
                        )
        return datalist

    def get_data(self, **kwargs):
        """ Returns List with padded arrays. If given data holding element is
            of type iterator, all elements will be polled.
        """
        datalist = self._element.get_data(*kwargs)
        max_dur = 0

        if type(datalist) != list:
            tmp = [container for container in datalist]
            datalist = tmp

        for container in datalist:
            if container.samples > max_dur:
                max_dur = container.samples

        return self._return(datalist, max_dur)


class RectificationDecorator(AbstractDataDecorator):
    """ Rectifies data by taking absolute value

        Attributes:
            element (DataHoldingElement): Element inheriting from
                ``DataHoldingElement`` or providing function ``get_data``
            is_iterator (bool): Indicates whether decorator is a generator
                or returns a list.
    """
    def __init__(self, data_holding_element, as_iterator=False):
        """ Initializes object
            Args:
                data_holding_element (model.model.DataHoldingElement): Any
                    instance whose class inhertis from
                    model.model.DataHoldingElement or provides same functions
                    and return values as defined in this class.

                as_iterator (boolean): If true object acts like an interator
        """
        super(RectificationDecorator, self).__init__(data_holding_element, as_iterator)

    def _iterate(self, elements):
        """ Yields rettified data

            Yields:
                DataContainer
        """
        for element in elements:
            element.data = np.abs(element.data)
            yield element

    def _return(self, elements):
        """ Returns List of rectified data

            Args:
                elements (Iterable): Iterable object yielding model.DataContainer

            Returns:
                List of model.DataContainer
        """
        ret = []
        for element in elements:
            element.data = np.abs(element.data)
            ret.append(element)
        return ret

    def get_data(self, **kwargs):
        """ Rectifies data. Returns list or iterator depending on
            attribute ``is_iterator``

            Args:
                kwargs (Dictionary): arguments for other methods

            Returns:
                Iterator or List
        """
        dataelement = self._element.get_data(**kwargs)

        if self._is_iterator:
            return self._iterate(dataelement)
        else:
            return self._return(dataelement)


class SubscriberDecorator(AbstractDataDecorator):
    """ Wraps an subscriber from package ``online.subscriber`` to use data received
        by subscriber with Decorators

        Attributes:
            subscriber (online.subscriber.Subscriber): Subscriber yielding data
    """

    def __init__(self, subscriber):
        """ Initializes object
            Args:
                subscriber (online.subscriber.Subscriber): Subscriber yielding data
        """
        super(PadzeroDecorator, self).__init__(None, True)
        self._subscriber = subscriber 

    def get_data(self):
        """ Returns a generator yielding DataContainer obtained from subscriber

            Returns:
                Generator
        """
        while True:
            message = self._subscriber.queue.get()
            parsed = ArrayMessage.deserialize(message)
            self._subscriber.queue.task_done()
            yield DataContainer.from_array(
                parsed.data,
                int(parsed.data.shape[0] / ArrayMessage.duration)
            )
    
