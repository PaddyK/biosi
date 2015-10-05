#!/bin/bash
""" This module implements the model (along the lines of the MVC pattern) for EMG
    projects.
    With model the class model defining the different components an EMG experiment is
    made up of.
    To create a model for an experiment a knowledge databse has to be specified. This can
    be done in an extra python file or somewhere else.
    To provide the data, either pass an already exsiting DataFrame to the model or specify
    files from which the data should be retrieved.
    The model servers than as interface to the DataFrame.

    Experiment:
        Main class.  Contains references to Subject, session and Subject. This class
        bundles all resources and makes them available to other components

    Subject:
        This class defines a subject participating in an experiment.

    session:
        This class defines a through setup, subjcet and time defined production of one
        or multiple recordings. Naturally it has a reference to the subjects and setup
        it is defined by and the experiment it belongs to.

    Setup:
        Defines the conditions a session is conducted by. Especially, the different
        groups of sensors employed are defined.
        The class contains a reference to session and Experiment.

    Subject:
        A subject participating in an experiment by going through one or multiple sessions

    Modality:
        Group(s) of sensors. A modality could for example be all the sensors located
        on the arm and a second one all those on the stomach.

    Channel:
        A sensor measuring one specific muscle.

    Recording:
        The output of the EMG. During a session one or multiple recordings might be
        produced.

    Trial:
        A part of a recording or a whole recording. A trial could either be a recording
        in its own right, i.e. referencing measurement values or it could simply be a
        set of pointers pointing to the start and end of the trial in one large recording.

    Note:
        When working with data be aware that everything is by reference. A DataFrame object
        retrieved from trial is not a copy of a part of the data of the recording the
        trial belongs to, but a view.
        If the trial's data is changed so is the data of the recording (and with that I
        mean the original data you may have passed to the recording during instantiation.

        Example:
            Took the freedome to add lines to the printout of DataFrame to make it more
            comprehensible:

            >>> arr = np.ndarray(
                    [1,2,3],
                    [4,5,6],
                    [7,8,9],
                    [10,11,12],
                    [13,14,15]
                )
            >>> recording = model.Recording(..., data = arr, ...)
            >>> trial = model.Trial(recording, 3, 3)
            >>> trial.Data
             | 0  1  2
            ----------
            2| 7  8  9
            3|10 11 12
            4|13 14 15
            >>> trial.Data = trial.Data * 10
            >>> trial.Data
             |  0   1   2
            -------------
            2| 70  80  90
            3|100 110 120
            4|130 140 150
            >>> recording.Data
             |  0   1   2
            -------------
            2| 70  80  90
            3|100 110 120
            4|130 140 150
            >>> recording.get_all_data()
             |  0   1   2
            -------------
            0|  1   2   3
            1|  4   5   6
            2| 70  80  90
            3|100 110 120
            4|130 140 150
            >>> arr
            array([[  0,   1    2],
                   [  4,   5    6],
                   [ 70,  80,  90],
                   [100, 110, 120],
                   [130, 140, 150])
"""

import numpy as np
import pandas as pd
import sys
import cPickle as pkl
import warnings

class DataContainer(object):
    """ Wrapper for a pandas.core.DataFrame to support additional
        functionality
    """

    def __init__(self, dataframe, frequency):
        """ Initialises object. For alternative constuctors see classemthods

            Args:
                dataframe (pandas.core.DataFrame): Frame containing data
                frequency (int): Sampling-Rate with which data was recorded
        """
        self._dataframe = dataframe
        self._frequency = frequency
        self._events = None

    @classmethod
    def from_array(cls, array, frequency, columns=None):
        """ Alternative constructor, creates element from numpy array

            Args:
                array (numpy.ndarray): Array containing data
                frequency (int): Frequency with wich data was recorded
                columns (List, optional): Names of features

            Returns:
                model.model.DataContainer
        """
        df = pd.DataFrame(array)
        if columns is not None:
            df.columns = columns
        return DataContainer(df, frequency)

    @property
    def columns(self):
        """ Returns headers of data

            Returns:
                List
        """
        return self._dataframe.columns

    @property
    def data(self):
        """ Returns data as numpy array

            Returns:
                numpy.ndarray
        """
        return self._dataframe.values

    @data.setter
    def data(self, values):
        """ Sets data of wrapped pandas.core.DataFrame. Requires values to have
            the same dimension on the second axis as original values

            Args:
                values (np.ndarray): New values

            Raises:
                AssertionError, if ``values`` has wrong second dimension
        """
        assert values.ndim == 2, 'model.model.DataContainer.data (setter): ' + \
                'Argument ``values`` has wrong number of dimensions. ' + \
                'Two dimensions are expected, {} dimensions are received'.format(
                     values.ndim)
        assert values.shape[1] == self.dataframe.shape[1], 'model.model.' + \
                'DataContainer.data (setter): Second axis has wrong number of' + \
                'dimensions. Expcted are {}, received are {}'.format(
                        self.dataframe.shape[1], values.shape[1])
        self._dataframe = pd.DataFrame(values, columns=self.dataframe.columns)

    @property
    def dataframe(self):
        """ Returns wrapped dataframe

            Returns:
                pandas.core.DataFrame
        """
        return self._dataframe

    @property
    def duration(self):
        """ Returns duration of data in seconds
        """
        # calculate duration anew every time since duration might change depending
        # on applied data transformations
        return float(self.dataframe.shape[0]) / float(self.frequency)

    @property
    def events(self):
        """ Returns list of events defined for data

            Returns:
                List of model.model.Event
        """
        return self._events

    @events.setter
    def events(self, events):
        """ Sets ``events`` attribute of DataContainer

            Args:
                events (List): List of model.model.Event objects
        """
        self._events = events

    @property
    def frequency(self):
        """ Return frequency

            Returns:
                int
        """
        return self._frequency

    def __getitem__(self, slice):
        """ Returns slice along first and second dimension. First dimension
            must be a numeric slice object. Second dimension must be a list
            of column names.

            Args:
                slice (float, Slice): Integer (point in time) or slice (duration).
                    values are expected in seconds.

            Note:
                Values of slic is expected in seconds. Floating point numbers
                are accepted, however the true indices are calculated using the
                frequency of this container and then cast to integer.
                Step argument is ignored.

            Example:
                To retrieve data from second 5.2 to 8.6 of channels ``channel1``
                and ``channel2`` of DataContainer ``container``:
                >>> container[5.2:8.6, ['channel1', 'channel2']

            Returns:
                model.model.DataContainer

            Raises:
                TypeError if argument ``slice`` is/contains negative values
                    or is larger than duration of data
        """
        columns = None
        container = None

        if type(slice) is tuple:
            slice, columns = slice

        if type(slice) is int:
            start = int(slice * self.frequency)
            stop = start + 1
        elif slice.start is None and slice.stop is None:
            start = 0
            stop = int(self.duration * self.frequency)
        else:
            start = int(slice.start * self.frequency)
            stop = int(slice.stop * self.frequency)

        assert start >= 0, 'model.model.DataContainer.__getitem__: ' + \
                'negative value for start of slice encountered. Must be positive'
        assert stop >= 0, 'model.model.DataContainer.__getitem__: ' + \
                'negative value for stop of slice encountered. Must be positive'
        assert start <= self.samples, 'model.model.DataContainer.' + \
                '__getitem__: Requested Timestamp larger than duration. ' + \
                'duration is: {}, requested startpoint was: {}'.format(
                        self.duration, float(start)/self.frequency
                        )
        # subtract 1 because counting starts at zero. Also allows slicing
        # to the end of the data by giving the duration as endpoint
        assert stop - 1 <= self.samples, 'model.model.DataContainer.' + \
                '__getitem__: Requested Timestamp larger than duration. ' + \
                'duration is: {}, requested startpoint was: {}'.format(
                        self.duration, float(stop)/self.frequency
                        )
        if columns is not None:
            for col in columns:
                assert col in self.dataframe.columns, ('Column {} is not in ' + \
                        'data container').format(col)

        if columns is None:
            dat = self.data[start:stop, :]
            container = DataContainer.from_array(dat, self.frequency, self.columns)
        else:
            dat = self.dataframe.iloc[start:stop, :]
            dat = dat.loc[:, columns]
            dat.reset_index(inplace=True, drop=True)
            container = DataContainer(dat, self.frequency)
        return container

    @property
    def num_channels(self):
        """ Returns number of channels

            Returns:
                int
        """
        return self.dataframe.shape[1]

    def one_hot_event(self, event_name):
        """ Returns a one-hot array with the same first dimension as DataContainer.
            Time steps of the event are set to one.

            Args:
                event_name (String): Name of event

            Returns:
                numpy.ndarray

            Raises:
                AssertionError if no events are defined
                KeyError if ``event_name`` could not be found
        """
        assert len(self.events) > 0, 'No events defined for DataContainer'
        exists = False
        onehot = np.zeros(self.samples, dtype=np.float)
        for event in self.events:
            if event.name == event_name:
                exists = True
                start = int(event.start * self.frequency)
                if event.duration is None:
                    stop = start + 1
                else:
                    stop = int((event.start + event.duration) * self.frequency)
                onehot[start:stop] = 1
        if not exists:
            raise KeyError('Event with name {} could not be found'.format(event_name))
        return onehot

    def __setitem__(self, slice, data):
        """ Sets values of DataContainer defined by slice.

            Args:
                slice (float, Slice): Integer (point in time) or slice (duration).
                    values are expected in seconds.
                data (array like): New Data of the same shape as defined by
                    slice and original data

            Note:
                Values of slic is expected in seconds. Floating point numbers
                are accepted, however the true indices are calculated using the
                frequency of this container and then cast to integer.
                Step argument is ignored.

            Raises:
                TypeError if argument ``slice`` is/contains negative values
                    or is larger than duration of data
        """
        if type(slice) is int:
            start = int(slice * self.frequency)
            stop = start + 1
        elif slice.start is None and slice.stop is None:
            start = 0
            stop = int(self.duration * self.frequency)
        else:
            start = int(slice.start * self.frequency)
            stop = int(slice.stop * self.frequency)

        assert start >= 0, 'model.model.DataContainer.__setitem__: ' + \
                'negative value for start of slice encountered. Must be positive'
        assert stop >= 0, 'model.model.DataContainer.__setitem__: ' + \
                'negative value for stop of slice encountered. Must be positive'
        assert start <= self.samples, 'model.model.DataContainer.' + \
                '__setitem__: Requested Timestamp larger than duration. ' + \
                'duration is: {}, requested startpoint was: {}'.format(
                        self.duration, float(start)/self.frequency
                        )
        # subtract 1 because counting starts at zero. Also allows slicing
        # to the end of the data by giving the duration as endpoint
        assert stop - 1 <= self.samples, 'model.model.DataContainer.' + \
                '__setitem__: Requested Timestamp larger than duration. ' + \
                'duration is: {}, requested startpoint was: {}'.format(
                        self.duration, float(stop)/self.frequency
                        )
        self.dataframe.iloc[start:stop, :] = data

    @property
    def samples(self):
        """ Returns number of samples (timesteps)

            Returns:
                int
        """
        return self.dataframe.shape[0]

    @property
    def shape(self):
        """ Returns shape of underlying data structure

            Returns:
                Shape object
        """
        return self.dataframe.shape


class Event(object):
    """ Models event in trial. Can also be used to model labels.

        Attributes:
            name (String): Name of event
            start (float): Starttime of event in seconds
            duration (float): Duration of event in seconds
    """

    def __init__(self, name, start, duration=None):
        self._name = name
        self._start = start
        self._duration = duration

    @property
    def duration(self):
        return self._duration

    @property
    def name(self):
        return self._name

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        """ Sets new start time of event.

            Args:
                start (float): Start point in seconds
        """
        self._start = start

    def to_string(self):
        str = 'Event {} at {}s'.format(self.name, self.start)
        if self.duration is not None:
            str += ' duration {}s'.format(self.duration)
        return str


class DataHoldingElement(object):
    def __getitem__(self, key):
        """ Returns data over time. Start, Stop, Step in seconds
        """
        pass

    def aslist(**kwargs):
        """ Returns all trials contained as list
        """
        pass

    def get_data(**kwargs):
        """ Returns result of Decorator operation.

            By default result of aslist() is returned.
        """
        return self.aslist(**kwargs)


class Experiment(DataHoldingElement):
    """ Representation of an EMG experiment. This class pools all information to reject
        or accept a hypothesis.

        Attributes:
            setups (Dictionary): Dictionary of Setup objects. Contains all technical
                specification with which EMG measurements were undertaken
            sessions (Dictionary): Dictionary of session objects. Contains all sessions
                conducted during the course of this experiment.
            subjects (Dictionary): Dictionary of Subject objects. Contains all subjects
                having participated in this experiment.
            session_order (List): List of strings. Storing order sessions were added
    """

    def __init__(self):
        self._setups = {}
        self._sessions = {}
        self._subjects = {}

        self._session_order = []

    @property
    def setups(self):
        return self._setups

    @property
    def sessions(self):
        return self._sessions

    @property
    def subjects(self):
        return self._subjects

    def get_data(self, modality, sessions=None):
        """ Returns all trials of a specific modality from all recordings of
            all sessions of, if argument ``sessions`` is set, only from a
            selection.

            Args:
                modality (String): Identifier of an modality. Only data of recordings
                    with this modality are returned
                sessions (List, optional): List of Strings. If set data for specified recordings
                    are returned, else data of all recordings are returned.

            Returns:
                List of model.model.DataContainer
        """
        trials = []
        if sessions is None:
            sessions = self._session_order

        for s in sessions:
            session = self.sessions[s]
            if modality not in session.setup.modalities.keys():
                continue
            trials.extend(session.get_data(modality=modality))
        return trials

    def get_data_by_labels(self, sessions=None, recordings=None, labels=None, as_list=True,
            pandas=True):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                sessions (list, optional): List of session Ids
                labels (list, optional): List with class labels
                recordings (list, optional): List of identifiers of recordings
                as_list (boolean, optional): Wether to return labels and
                    sequence as lists
                pandas (boolean, optional): Whether to return data as
                    pandas.core.frame.DataFrame or as numpy.ndarray

            Returns:
                sequences, List, Pandas data frame or numpy ndarray
                labels, List, Pandas data frame or numpy ndarray
        """
        if sessions is None:
            sessions = self._session_order

        sequences = None
        labels = None
        for session in sessions:
            if session in self._session_order:
                d, l = self.sessions[session].get_data_by_labels(
                        labels=labels,
                        recordings=recordings,
                        as_list=as_list,
                        pandas=pandas
                        )
                if sequences is None:
                    sequences = d
                    labels = l
                elif as_list:
                    sequences.extend(d)
                    labels.extend(l)
                elif pandas:
                    sequences = pd.concat([sequences, d])
                    labels = pd.concat([labels, l])
                else:
                    sequences = np.concatenate([sequences, d])
                    labels = np.concatenate([labels, l])
        return sequences, labels

    def get_frequency(self, setup=None, modality=None):
        """ Returns frequency of one modality of one session.

            Args:
                setup (string, optional): Identifier of one session
                modality (string, optional): Identifier of one modality

            Note:
                If one setup is defined only, setup does not need to be set. Same goes for
                modality.

            Raises:
                ValueError: If more than one setup is defined and `setup` argument not set
                ValueError: If in setup `setup` more than one modality is defined
                    but `modality` argument not set

            Returns:
                frequency (int)
        """
        f = None
        if setup is None:
            if len(self.setups) > 1:
                raise ValueError((
                    'More than one Setup defined but none specified. Specify ' +
                    'setup to retrieve frequency'
                ))
            else:
                f = self.setups[self.setups.keys()[0]].get_frequency(modality)
        else:
            f = self.setups[setup].get_frequency(modality)

        return f
        for setup in self.setups.itervalues():
            if f == 0:
                f = setup.frequency
            if f != setup.frequency:
                raise ValueError('Different frequencies used during Experiment')

        return f

    def get_int_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                labels (List): List of integers
                mapping (Dictionary): Mapping label (string) to integer
        """
        labels = self.get_labels()
        ilabels = []
        mapping = {}
        count = 0
        for lbl in labels:
            if lbl in mapping:
                ilabels.append(mapping[lbl])
            else:
                mapping[lbl] = count
                count = count + 1
                ilabels.append(count)
        return ilabels, mapping

    def get_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                List of Strings
        """
        labels = []
        for t in self._session_order:
            labels.extend(self.sessions[t].get_labels())

        return labels

    def get_event(self, modality, sessions=None, from_=None, to=None):
        """ Returns all event in an specific interval from one/multiple/all
            sessions of this experiment.
            If event to multiple sessions are returned an offset is added to the time of each
            event according to the order in which each sessions is listed in `sessions`.
            It is assumed, that data of sessions are retrieved in the same order.

            Args:
                modality (String): Identifier of an modality. Only events of recordings
                    with this modality are returned
                sessions (List): List of Strings. If set events for specified recordings
                    are returned, else events of all recordings are returned.
                from_ (float): Start point from which on events should be retrieved
                to (float): End point of event retrieval

            Note:
                `from_` and `to` operate over the accumulated length of specified recordings.
                So if events from all recordings should be selected, but `from_` and `to`
                are very small recordings will be excluded.

            Returns:
                events (List): List of tuples containing obejcts of type Event
        """
        duration = 0
        recordings = None

        if sessions is None:
            sessions = self._session_order

        if from_ is None:
            from_ = 0
        elif from_ < 0:
            raise IndexError('Start point of time interval out of bounds')

        if to is None:
            to = duration
        elif to < 0:
            raise IndexError('End point of time interval out of bounds')

        ret = []
        offset = 0
        to_pass = 0
        for s in sessions:
            to_pass = 0
            from_pass = 0
            s_dur = self.sessions[s].get_duration(modality=modality)
            if from_ > offset + s_dur:
                # Start point of interval larget than duration of first n recocdings
                # exclude recording and continue
                continue
            elif (from_ > offset) and (from_ < offset + s_dur):
                # If start point of interval lies within nth recording start retrieving
                # from this point. Convert to relative start of recording
                from_pass = from_ - offset

            if to < offset:
                # If accumulated duration of all recordings is larger than end point
                # of time interval stop retrieving events
                break
            elif (to > offset) and (to < offset + s_dur):
                # If end of time interval lies within one recording retrieve only
                # events until relative point of time in recording
                to_pass = to - offset

            events = self.sessions[s].get_event(from_=from_pass, to=to_pass)
            for e in events:
                ret.append(Event.new_time(e, e.start + offset))
            offset = s_dur + offset
        return ret

    def get_recording(self, identifier, session):
        """ Returns specified recording if it exists

            Args:
                identifier (string): Identifier of the recording (name it was given)
                session (string, optional): Identifier of the session recording belongs
                    to. If not specified, all sessions will be searched

            Returns:
                If successful return Recording

            Raises:
                IndexError: If no *recording* with ``Identifier`` or no *session*
                with identifier ``session`` exists
        """
        recording = None
        if session is None:
            for s in self.sessions.iteritems():
                try:
                    recording = s.get_recording(identifier)
                except IndexError:
                    pass
                except:
                    print 'Unexpected Error:', sys.exec_info()[0]
            if recording is None:
                raise IndexError((
                    'Recording with identifier ' + identifier + ' is not part ' +
                    'of any session' % (identifier)
                ))
        else:
            if session not in self.sessions:
                raise IndexError('Experiment has no session %s', (session))
            else:
                recording = self.sessions[session].get_recording(identifier)
        return recording

    def get_trial(self, identifier, session, recording):
        """ Retrieves a trial

            Args:
                identifier (string): Identifier of the trial (name given)
                session (string): Identifier of the session trial belongs to
                recording (string): Identifier of recording trial belongs to

            Returns:
                Trial object if successful

            Raises:
                IndexError: If there does not exist a session, Recording or Trial with
                Identifier ``session``, ``recording`` or ``trial``
        """
        trial = None
        if session not in self.sessions:
            raise IndexError('Experiment has no session with identifier %s' % (session))
        elif recording is None:
            for rc in self.sessions[session].recordings.iteritems():
                if identifier in rc.trials:
                    trial = rc.get_trial(identifier)
            if trial is None:
                raise IndexError((
                    'No trial with identifier %s exists in any recording of ' +
                    'session %s' % (identifier, session)
                ))
        else:
            rc = self.get_recording(recording, session)
                # throws error if recording does not exist.
            trial = rc.get_trial(identifier)

        return trial

    def put_setup(self, setup):
        if setup.identifier not in self.setups:
            self.setups[setup.identifier] = setup
        else:
            raise IndexError((
                'Setup with identifier ' + setup.identifier + ' already exists in ' +
                ' experiment'
            ))

    def put_session(self, session):
        if session.identifier not in self.sessions:
            self.sessions[session.identifier] = session
            self._session_order.append(session.identifier)
        else:
            raise IndexError((
                'session with identifier ' + session.identifier + ' already exists in ' +
                ' experiment'
            ))

    def put_subject(self, subject):
        if subject.identifier not in self.subjects:
            self.subjects[subject.identifier] = subject
        else:
            raise IndexError((
                'Subject with identifier ' + subject.identifier + ' already exists in ' +
                ' experiment'
            ))

    def to_string(self):
        return (
            'Experiment: %d Setups, %d sessions, %d Subjects' %
            (len(self.setups), len(self.sessions), len(self.subjects))
        )

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        string =  string + 'Subjects:\n'
        for s in self.subjects.itervalues():
            string = string + '\t' + s.to_string() + '\n'
        string = string + 'Setups:\n'
        for s in self.setups.itervalues():
            tmp = s.recursive_to_string()
            string = string + '\t' + tmp.replace('\n','\n\t') + '\n'
        string = string + 'sessions:\n'
        for s in self.sessions.itervalues():
            tmp = s.recursive_to_string()
            string = string + '\t' + tmp.replace('\n', '\n\t') + '\n'
        return string


class Subject(object):
    """ Represents subjects having paricipated in the course of an EMG experiment.

        Attributes:
            identifier (string): Identifier of a subject
    """
    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def identifier(self):
        return self._identifier

    def to_string(self):
        return self.identifier


class Setup(object):
    """ Represents a setup for an session. Specifies the amount and
        grouping of sensors of different recording systems.
    """

    def __init__(self, experiment, identifier = None):
        self._identifier = identifier
        self._modalities = {}
        self._experiment = experiment
        self._features = 0
        self._modality_order = []

        if self._identifier is None:
            self._identifier = 'setup' + str(len(self._experiment.setups))

        self._experiment.put_setup(self)

    def get_frequency(self, modality = None):
        """ Returns the frequency of a specified modality.

            Args:
                modality (String): Identifier of maodality for which  frequency should be
                    retrieved.

            Note:
                If only one modality is defined, `modality` argument does not need to
                be set.

            Raises:
                ValueError: If more than one modality is defined and `modality` argument
                    not set.

            Returns:
                frequency (int): frequency (SamplingRate) of a modality
        """

        f = None
        if modality is None:
            if len(self.modalities) > 1:
                raise ValueError((
                    'More than one modality defined. Specify modality for which' +
                    'to retrieve frequency'
                ))
            else:
                f = self.modalities[self._modality_order[0]].frequency
        else:
                f = self.modalities[modality].frequency

        return f

    @property
    def identifier(self):
        return self._identifier

    @property
    def modalities(self):
        return self._modalities

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, features):
        self._features = features

    def get_channel_order(self):
        order = []
        for idx in self._modality_order:
            order.extend(self.modalities[idx].channel_order)
        return order

    def put_modality(self, modality):
        if modality.identifier not in self.modalities:
            self.modalities[modality.identifier] = modality
            self._modality_order.append(modality.identifier)
        else:
            raise IndexError((
                'Modality with identifier ' + modality.identifier + ' already exists ' +
                'in Setup ' + self.identifier
            ))

    def to_string(self):
        return (
            'Setup %s: %d modalities' %
            (self.identifier, len(self.modalities))
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() +'\n'
        for m in self.modalities.itervalues():
            tmp = m.recursive_to_string().replace('\n', '\n\t')
            string = string + '\t' + tmp + '\n'
        return string


class Modality(object):
    """ Represents a modality. A modality in the context of EMG is a group of sensors, for
        example on the hand. Another modality would be a second set of sensors on the breast.

        Also modality could be another kind of recording system such as EEG

        Args:
            setup (Setup): Setup this modality is specified in
            identifier (string, optional): Identifier for this modality. Later usable to
                select a specific instance. If not specified replaced by a generic one

        Attributes
            setup (Setup): Setup this modality is specified in
            identifier (string): Identifier for this modality. Later usable to select one
                specific instanace
            channels (Dictionary): Dictionary of channels i.e. sensors making up modality
            frequency (int): frequency (Sampling-Rate) at which data points are taken
    """

    def __init__(self, setup, frequency, identifier = None):
        self._setup = setup
        self._identifier = identifier
        self._frequency = frequency
        self._channels = {}
        self._channel_order = []

        if self._identifier is None:
            self._identifier = 'modality' + str(len(self._setup.modalities))

        self._setup.put_modality(self)

    @property
    def identifier(self):
        return self._identifier

    @property
    def frequency(self):
        return self._frequency

    @property
    def channels(self):
        return self._channels

    @property
    def setup(self):
        return self._setup

    @property
    def num_channels(self):
        """ Returns number of defined channels

            Returns:
                int
        """
        return len(self._channels)

    @property
    def channel_order(self):
        """ Returns List of identifiers in order in which they were added

            returns:
                List of Strings
        """
        return self._channel_order

    def add_channels(self, channels):
        """ Convenience function to add multiple channesl to one modality at
            once

            Args:
                channel (List): List of channel identifiers

            Note:
                order in which channels are defined is the order they are
                expected to appear in the data.
        """
        for channel in channels:
            Channel(self, channel)

    def get_channel_index(self, identifier=None):
        """ Returns index of channels specified in ``identifier``

            if ``identifier`` is None values 0..num Channels are returned

            Args:
                identifier (List, String): Either string or list of strings

            Returns:
                indices, List of integers

            Raises:
                ValueError if one of the specified identifier is not found
        """
        if identifier is None:
            return range(len(self.channel_order))

        if (type(identifier) == str) or (type(identifier) == unicode):
            identifier = [identifier]

        indices = []
        for id in identifier:
            indices.append(self.channel_order.index(id))
        return indices

    def put_channel(self, channel):
        if channel.identifier not in self.channels:
            self.channels[channel.identifier] = channel
            self.setup.features = self.setup.features + 1
            self._channel_order.append(channel.identifier)
        else:
            raise IndexError((
                'Channel with identifier ' + channel.identifier + ' already exists ' +
                'in Modality ' + self.identifier
            ))

    def to_string(self):
        string = (
            'Modality %s: %d Channels, %d Hz' % (self.identifier, len(self.channels), self.frequency)
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for s in self.channels.itervalues():
            string = string + '\t' + s.to_string() + '\n'
        return string


class Channel(object):
    """ Represents a channel i.e. sensor.

        Args:
            modality (Modality): Modality this channel belongs to
            identifier (string, optional): Identifier for this channel. If not set a
                generic one will be used. It is strongly recommended to use a identifier
                here.

        Attributes:
            modality (Modality): Modality this channel belongs to
            identifier (string): Identifier for this channel
    """

    def __init__(self, modality, identifier = None):
        self._modality = modality
        self._identifier = identifier

        if self._identifier is None:
            self._identifier = 'channel' + str(len(self._modality.channels))

        self._modality.put_channel(self)

    @property
    def identifier(self):
        return self._identifier

    def to_string(self):
        return 'Channel: ' + self.identifier


class Session(DataHoldingElement):
    """ Implements a session of an experiment. A session is defined by the subject
        participating, the used setup and the time it takes place.

        Args:
            experiment (Experiment): Experiment session belongs to
            setup (Setup): The setup used for this session
            subject (Subject): The subject participating in this session
            identifier (string, optional): Identifier of the session. If no identifier is
                provided a generic one will be used.

        Attributes:
            experiment (Experiment): Experiment session belongs to
            setup (Setup): The setup used for this session
            subject (Subject): The subject participating in this session
            identifier (string): Identifier of the session. If no identifier is provided
                a generic one will be used (session0, session1, ...).
            recordings (Dictionary): Dictionary of all recordings produced durint the
                session.
            recording_order (List): Stores order in which recordings were added
            samples (int): Count of samples of all recordings and trials part of
                a session
    """

    def __init__(self, experiment, setup, subject, identifier = None):
        self._identifier = identifier
        self._subject = subject
        self._setup = setup
        self._experiment = experiment
        self._recordings = {}
        self._recording_order = []
        self._samples = 0 # If a trial is added to a recording this count is alsoc incremented

        if self._identifier is None:
            self._identifier = 'session' + str(len(self._experiment.sessions))

        self._experiment.put_session(self)

    @property
    def subject(self):
        """ Returns subject object associated with session

            Returns:
                model.model.Subject
        """
        return self._subject

    @property
    def setup(self):
        """ Returns setup associated with session

            Returns:
                model.model.session
        """
        return self._setup

    @property
    def experiment(self):
        """ Returns experiment session belongs to

            Returns:
                model.model.Experiment
        """
        return self._experiment

    @property
    def recordings(self):
        """ Returns recordings for this session

            Returns:
                Dictionary of model.model.Recording
        """
        return self._recordings

    @property
    def identifier(self):
        """ Returns identifier of this session

            Returns:
                String
        """
        return self._identifier

    def add_events(self, events):
        """ Convenience function to add multiple events to recordings and
            trials at once.

            Args:
                events (Dictionary like): Dictionary or pandas.core.DataFrame
                    dictionary must use trial name as key and map to a 2D list
                    of the form ``[[<event name>, <start>, <duration>], [...]]``.
                    DataFrame must have trial identifier as column index.
                    columns must be in order ``<event name>``, ``<start>``,
                    ``<stop>``

            Note:
                start of each event must be relative to the **beginning of the
                trial** it belongs to.
        """
        for recording in self._recordings.itervalues():
            recording.add_events(trials)

    def add_trials(self, trials):
        """ Convenience function to add multiple trials at once.

            Args:
                trials (Arraylike): Two dimensional list, dataframe or numpy
                    array containing start, stop (or duration) and optional
                    identifier of trial.

            Note:
                trials must have the following structure:
                    (start, duration)
                optional are a third field containing trial's identifier.
                When using DataFrame, duration can be replaced by time trial
                ends. This columns must then be named `stop`.
        """
        for recording in self._recordings.itervalues():
            recording.add_trials(trials)

    def get_all_data(self):
        """ Returns all data from all recordings belonging to session

            Returns:
                pandas.core.DataFrame
        """
        df = None
        for idx in self._recording_order:
            if df is None:
                df = self.recordings[idx].get_all_data()
            else:
                df = pd.concat([df, self.recordings[idx].get_all_data()])
        return df

    def get_data_by_labels(self, recordings=None, labels=None, as_list=True,
            pandas=True):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                labels (list, optional): List with class labels
                recordings (list, optional): List of identifiers of recordings
                as_list (boolean, optional): Wether to return labels and
                    sequence as lists
                pandas (boolean, optional): Whether to return data as
                    pandas.core.frame.DataFrame or as numpy.ndarray

            Returns:
                sequences, List, Pandas data frame or numpy ndarray
                labels, List, Pandas data frame or numpy ndarray
        """
        if recordings is None:
            recordings = self._recording_order

        sequences = None
        labels = None
        for recording in recordings:
            if recording in self._recording_order:
                d, l = self.recordings[recording].get_data_by_labels(
                        labels=labels,
                        as_list=as_list,
                        pandas=pandas
                        )
                if sequences is None:
                    sequences = d
                    labels = l
                elif as_list:
                    sequences.extend(d)
                    labels.extend(l)
                elif pandas:
                    sequences = pd.concat([sequences, d])
                    labels = pd.concat([labels, l])
                else:
                    sequences = np.concatenate([sequences, d])
                    labels = np.concatenate([labels, l])
        return sequences, labels

    def get_data(self, modality=None):
        """ Returns trials of all recordings associated with ``modality``
            defined for this session.

            Args:
                modality (string, optional): Identifier of an modality. Required
                    for more than one modality present in session's setup.

            Returns:
                List of model.model.DataContainer
        """
        trials = []

        if (len(self.setup.modalities) > 1) and (modality is None):
            raise ValueError((
                'More than one modality present in setup {a} of session ' +
                '{s} but modality argument was not defined'
                ).format(a=self.setup.identifier, s=self.identifier)
            )
        elif (len(self.setup.modalities) == 1) and (modality is None):
            modality = self.setup.modalities.popitem()[1]

        df = None
        begin_pass = None
        end_pass = None
        stop = 0

        for idx in self._recording_order:
            if (self.recordings[idx].modality.identifier != modality):
                continue
            trials.extend(self.recordings[idx].get_data())
        return trials

    def get_frequency(self, modality):
        """ Returns frequency of setup

            Args:
                Modality for which frequency is going to be retrieved
        """
        return self.setup.get_frequency(modality=modality)

    def get_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                List of Strings
        """
        labels = []
        for t in self._recording_order:
            labels.extend(self.recordings[t].get_labels())

        return labels

    def get_event(self, recordings=None, from_=None, to=None):
        """ Returns all events in an specific interval from one/multiple/all
            recordings of this session.
            If multiple recordings are returned an offset is added to the time of each
            event according to the order in which each recording is listed in `recordings`.
            It is assumed, that data of recordings are retrieved in the same order.

            Args:
                recordings (List): List of Strings. If set events for specified recordings
                    are returned, else events of all recordings are returned.
                from_ (float): Start point from which on events should be retrieved
                to (float): End point of event retrieval

            Note:
                `from_` and `to` operate over the accumulated length of specified recordings.
                So if event from all recordings should be selected, but `from_` and `to`
                are very small recordings will be excluded.

            Returns:
                events (List): List of tuples containing objects of type Event
        """
        duration = 0
        if recordings is None:
            recordings = self._recording_order

        for rec in recordings:
            if rec in self._recording_order:
                duration = duration + self.recordings[rec].duration
            else:
                raise IndexError(
                    'No recording with identifier %s in session %s' %
                    (rec, self.identifier)
                )

        if from_ is None:
            from_ = 0
        elif (from_ < 0) and (from_ >= duration):
            raise IndexError('Start point of time interval out of bounds')

        if to is None:
            to = duration
        elif (to < 0) or (to > duration):
            raise IndexError('End point of time interval out of bounds')

        ret = []
        offset = 0
        to_pass = 0
        for rec in recordings:
            to_pass = 0
            from_pass = 0
            rec_dur = self.recordings[rec].duration
            if from_ > offset + rec_dur:
                # Start point of interval larget than duration of first n recocdings
                # exclude recording and continue
                continue
            elif (from_ > offset) and (from_ < offset + rec_dur):
                # If start point of interval lies within nth recording start retrieving
                # from this point. Convert to relative start of recording
                from_pass = from_ - offset

            if to < offset:
                # If accumulated duration of all recordings is larger than end point
                # of time interval stop retrieving event
                break
            elif (to > offset) and (to < offset + rec_dur):
                # If end of time interval lies within one recording retrieve only
                # event until relative point of time in recording
                to_pass = to - offset

            events = self.recordings[rec].get_event(from_=from_pass, to=to_pass)

            for e in events:
                ret.append(Event.new_time(e, e.start + offset))

            offset = offset + rec_dur

        return ret

    def get_recordings(self, modality):
        """ Returns all recordings belonging to a specific modality

            Args:
                modality (String): Identifier of an modality

            Returns:
                recordings (List): List of recording in the order in which they were added
        """
        ret = []
        for rid in self._recording_order:
            if modality == self.recordings[rid].modality:
                ret.append(self.recordings[rid])

        if len(ret) == 0:
            warnings.warn('No recording found recorded with modality %s' % modality)

        return ret

    def get_recording(self, identifier):
        if identifier not in self.recordings:
            raise IndexError(
                'No recording with identifier %s in session %s' %
                (identifier, self.identifier)
            )
        else:
            return self.recordings[identifier]

    def put_recording(self, recording):
        """ Appends one recording to object attribute *recordings*

            Params:
                recording (Recording): Recording to associate with session
        """
        if recording.identifier not in self.recordings:
            self.recordings[recording.identifier] = recording
            self._recording_order.append(recording.identifier)
        else:
            raise IndexError((
                'Recording with identifier ' + recording.identifier + ' already exists' +
                ' in session ' + self.identifier
            ))

    def put_recordings(self, recordings):
        """ Appends a list of recordings to object attribute *recordings*

            Params:
                recordings (list): List of recordings
        """
        for rc in recordings:
            self.put_recording(rc)

    def to_string(self):
        string = (
            'session %s: Subject %s, Setting %s, %d recordings' %
            (
                self.identifier,
                self.subject.identifier,
                self.setup.identifier,
                len(self.recordings)
            )
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for r in self.recordings.itervalues():
            tmp = r.recursive_to_string().replace('\n','\n\t')
            string = string + '\t' + tmp + '\n'
        return string


class Recording(DataHoldingElement):
    """ Represents one recording of a session. May contain multiply trials, i.e. performed
        tasks.

        Args:
            session (session): The session in which recording was recorded
            modality (model.model.Modality): Modality recording is associated
                with. Set if multiple modalities (e.g. eeg, emg) are used
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with channels of this recording.
            identifier (string, optional): Identifier of one instance

        Note:
            Either ``data`` or ``location`` has to be set. If both are set, ``location``
            is ignored, data is not read from file.

        Attributes:
            session (session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with channels of this recording.
            duration (float): duration of recording in data in seconds
            samples (int): Number of samples in this recording. The sum of all sample
                counts of trials being part of this recording
            trials (Dictionary): Trials included in this recording.
            identifier (string): Identifier of one specific instance
            features (int): Number of features in data set
            trial_order (List): Stores order in which trials were added
            modality (String): Modality recording is associated with
            events (List): Sorted list of Events.
                in seconds. Second element is label. List is sorted after time

        Raises:
            ValueError: Raised if both, location and data are not set
    """

    def __init__(self, session, modality, location = None, data = None,
            identifier = None):
        self._session = session
        self._location = location
        self._samples = 0
        self._trials = {}
        self._identifier = identifier
        self._trial_order = []
        self._modality = modality
        self._events = []

        if self._identifier is None:
            self._identifier = 'recording' + str(len(self._session.recordings))

        if (data is None) and (location is None):
            raise ValueError('Neither location nor data set in Recording')

        if data is None:
            datactrl = DataController()
            data = datactrl.read_data_from_file(location)
        else:
            if type(data) is pd.DataFrame:
                data = data.values
            elif type(data) is np.ndarray:
                pass
            else:
                raise ValueError('Data is of unsupported type. Expected ' + \
                        '"numpy.ndarray or pandas.core.DataFrame. Got {}'
                        .format(type(data))
                        )
        self._data = DataContainer.from_array(
                data,
                self._modality.frequency,
                self._modality.channels
                )
        self._session.put_recording(self)

    @property
    def session(self):
        """ Returns session recording belongs to

            Returns:
                model.model.session
        """
        return self._session

    @property
    def location(self):
        """ Returns path to file data for recording is stored

            Returns:
                String
        """
        return self._location

    @property
    def trials(self):
        """ Returns Trials defined for Recording

            Returns:
                model.model.Trial
        """
        return self._trials

    @property
    def data(self):
        """ Property for data attribute

            Returns:
                model.model.DataContainer
        """
        return self._data

    @property
    def features(self):
        """ Return number of features

            Returns:
                int
        """
        return self._data.shape[1]

    @property
    def identifier(self):
        """ Returns identifier of this recording

            Returns:
                String
        """
        return self._identifier

    @property
    def modality(self):
        """ Returns Modality associated with this recording

            Returns:
                model.model.Modality
        """
        return self._modality

    def add_events(self, events):
        """ Convenience function to add multiple events to recording and
            trials at once.

            Args:
                events (Dictionary like): Dictionary or pandas.core.DataFrame
                    dictionary must use trial name as key and map to a 2D list
                    of the form ``[[<event name>, <start>, <duration>], [...]]``.
                    DataFrame must have trial identifier as column index.
                    columns must be in order ``<event name>``, ``<start>``,
                    ``<stop>``

            Note:
                start of each event must be relative to the **beginning of the
                trial** it belongs to.
        """
        def get_keys(toplevel):
            """ Returns trirals identifier as list """
            if type(toplevel) is dict:
                return toplevel.keys()
            elif type(toplevel) is pd.DataFrame:
                return toplevel.iloc[:, 0].unique().tolist()
            else:
                raise AttributeError('Unknwon type encountered in model.model' + \
                        '.Recording.add_events. Type {} not supported for ' + \
                        'argument events'.format(type(toplevel)))

        def yield_record(toplevel, key):
            if type(toplevel) is dict:
                for record in toplevel[key]:
                    yield record
            elif type(toplevel) is pd.DataFrame:
                sliced = toplevel.loc[toplevel.iloc[:, 0] == key]
                #sliced = sliced.drop_duplicates()
                for i in range(sliced.shape[0]):
                    yield sliced.iloc[i, 1:].values.tolist()

        for key in get_keys(events):
            for record in yield_record(events, key):
                self.trials[key].add_event(*record)

    def add_trials(self, trials):
        """ Convenience function to add multiple trials at once.

            Args:
                trials (Arraylike): Two dimensional list, dataframe or numpy
                    array containing start, stop (or duration) and optional
                    identifier of trial.

            Note:
                trials must have the following structure:
                    (start, duration)
                optional are a third field containing trial's identifier.
                When using DataFrame, duration can be replaced by time trial
                ends. This columns must then be named `stop`.
        """

        def yield_record(trials):
            if type(trials) is list:
                for trial in trials:
                    yield trial
            elif type(trials) is np.ndarray:
                for i in range(trials.shape[0]):
                    yield trials[i].tolist()
            elif type(trials) is pd.DataFrame:
                for i in range(trials.shape[0]):
                    record = trials.loc[i, :].values.tolist()
                    if 'stop' in trials.columns:
                        # if column stop exists calculate duration of trial
                        record[1] = record[2] - record[1]
                    yield record
            else:
                raise AttributeError('Unsupported type for argument trials ' + \
                        'in model.model.Recording.add_trials. Expected ' + \
                        'numpy.ndarray, pandas.core.DataFrame or list. ' + \
                        'ecountered {}'.format(type(trials)))

        for rec in yield_record(trials):
            if len(rec) == 2:
                rec.append(None)
            elif len(rec) != 3:
                raise ArgumnentError('Wrong number of arguments given for ' + \
                        'constructing trial in model.model.Recording.' + \
                        'add_trials. Expected 2 or three, got {}'.format(len(rec)))
            Trial(self, record[0], record[1], record[2])

    def get_event(self, from_=None, to=None):
        """ Returns events either for whole recording or for a specific time interval

            Note:
                The time slice is specified with respect to the duration of the
                *relevant* experiment. That is only the data specified by the
                trials.
                So if the recording has a length of 55s and each trial has a
                duration of 10s and starts with an offset of 5s (0s-10s trial 1
                15s-25s trial2, 30s-40s trial3, 45s-55s trial4) then the time
                slice `(5;15) includes the last 5s of trial1 and the first 5s
                of trial2 --> $$[5;10)\cup[10;15)$$

            Args:
                from_ (float, optional): Start of time interval for which events should be retrieved
                to (float, optional): End of time interval for which event should be retrieved

            Note:
                If either `from` or `to` is set alone, all events from `start` until
                end of recording or all events from beginning of recording until `to`
                are returned.

            Raises:
                IndexError: If either `_from` or `to` is higher than recording's duration
        """
        if from_ is None:
            from_ = 0
        elif from_ >= self.duration:
            raise IndexError('Start point of interval higher than duration of recording')

        if to is None:
            to = self.duration
        elif to > self.duration:
            raise IndexError('End point of interval higher than duration of recording')

        duration = 0
        offset = 0
        to_pass = None
        from_pass = None
        ret = []
        for trial in self._trial_order:
            offset = offset + duration
            duration = self.trials[trial].duration

            if from_ > offset + duration:
                continue
            elif (from_ > offset) and (from_ < duration + offset):
                from_pass = from_ - offset
            else:
                from_pass = None

            if to < offset:
                break
            elif (to > offset) and (to < duration + offset):
                to_pass = to - offset
            else:
                to_pass = None

            tmp = self.trials[trial].get_event(from_=from_pass, to=to_pass)
            for e in tmp:
                e.start = e.start + offset
                ret.append(e)

        return ret

    def get_data(self, begin=None, end=None):
        """ Returns the **relevant** data of a recording object. As a List of
            DataContainer objects.
            In especially, yields only the data specified in the trials belonging to the
            recording.
            If `begin` and `end` are specified only data contained in time interval is
            returned.

            Args:
                begin (float): Point of time in seconds of beginning of time interval
                end (float): Point of time in seconds of ending of time interval

            Example:
                Sampling rate of 4000Hz, recording is 60s long. Trial one goes from
                second 10 to second 30, and trial02 from second 35 to second 50.
                Then this function only yields the channels in the intervals 10..30 and
                35..50. So a total of (20 + 15) * 4000 channels instead of 60 * 4000 channels

            Returns:
                List of model.model.DataContainer
        """
        return_list = []
        if begin > end:
            raise ValueError((
                'Beginning of time interval larger than ending. Beginning was {beg},' +
                'end was {e}'
                ).format(beg=begin, e=end)
            )
        elif begin >= self.duration:
            raise ValueError((
                'Beginning of time interval larger than duration of recording {rec}. ' +
                'Start point of interval was at {a}s, duration is {b}s'
                ).format(a=begin, b=self.duration)
            )
        elif end > self.duration:
            raise ValueError((
                'End of time interval larger than duration of recording {rec}. ' +
                'Start point of interval was at {a}s, duration is {b}s'
                ).format(a=end, b=self.duration)
            )
        # New data frame is created
        begin_pass = None
        end_pass = None
        stop = 0

        for idx in self._trial_order:
            offset = stop # Offset has to be set here to ensure its set
                          # even if continue clause is executed!
            stop = offset + self.trials[idx].duration

            if begin is not None:
                if begin > stop:
                    continue
                elif (begin > offset) and (begin < stop):
                    begin_pass = begin - offset
                else:
                    begin_pass = None

            if end is not None:
                if end < offset:
                    break
                elif (end > offset) and (end < stop):
                    end_pass = end - offset
                else:
                    end_pass = None

            return_list.append(self.trials[idx].get_data(begin=begin_pass, end=end_pass))
        return return_list

    def _label_to_data_pandas(self, trials, labels):
        """ Given a list of trials and a list of labels returns one DataFrame
            containing all the data of trials and one DataFrame with a label
            for each channel in the trial's DataFrame.

            I.e. The first axis of the returned DataFrames is the same.

            Args:
                trials (List): List of model.model.Trials
                labels (List): List of labels (strings). One label for each trial

            Returns:
                pd_trials (pandas.core.frame.DataFrame)
                pd_labels (pandas.core.frame.DataFrame)
        """
        pd_trials = trials[0]
        pd_labels = pd.DataFrame(
                [labels[0] for i in range(trials[0].shape[0])]
                )
        for i in range(1, len(trials)):
            pd_trials = pd.concat([pd_trials, trials[i]])
            pd_labels = pd.concat([
                pd_labels,
                pd.DataFrame(
                    [labels[i] for j in range(trials[i].shape[0])]
                    )
                ])
        return pd_trials, pd_labels

    def _label_to_data_numpy(self, trials, labels):
        """ Given a list of trials and a list of labels returns one ndarray
            containing all the data of trials and one ndarray with a label
            for each channel in the trial's ndarray.

            I.e. The first axis of the returned ndarrays is the same.

            Args:
                trials (List): List of model.model.Trials
                labels (List): List of labels (strings). One label for each trial

            Returns:
                np_trials (numpy.ndarray)
                np_labels (numpy.ndarray)
        """
        np_trials = trials[0]
        np_labels = np.array(
                [labels[0] for i in range(trials[0].shape[0])]
                )
        for i in range(1, len(trials)):
            np_trials = np.row_stack([np_trials, trials[i]])
            lst = [labels[i] for j in range(trials[i].shape[0])]
            a = np.array(lst)
            np_labels = np.concatenate([np_labels, a])
        return np_trials, np_labels

    def get_data_by_labels(self, labels=None, as_list=True, pandas=True):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                labels (list, optional): List with class labels. If not set
                    data to all labels is returned
                as_list (boolean, optional): Return trials in list (List of
                    array like) and labels as list (list of strings)
                pandas (boolean, optional): Return trials and data as
                    pandas.core.frame.DataFrame or as numpy.ndarray

            Note:
                If `as_list=False` trials are stacked to one big DataFrame/array.
                Labels are also returned as one big DataFrame/Array and repeated
                as often as trial has channels.
                So the first dimension of `labels` and `data is the same.

                If `as_list=True` trials are in one list (as DataFrame or array
                depending on argument `pandas`. Labels are also returned as list
                **but not replicated**. So its only a list of strings **and not**
                a list of DataFrames/arrays.

            Returns:
                data (List/array like)
                labels (List/array like)
        """
        if labels is None:
            labels = self.get_labels()

        trials = []
        ret_labels = []

        for idx in self._trial_order:
            if self.trials[idx].Label in labels:
                trials.append(self.trials[idx].get_data(pandas=pandas))
                ret_labels.append(self.trials[idx].Label)

        for lbl in ret_labels:
            if lbl not in ret_labels:
                warnings.warn(
                    'Label %s was not found in any trial of recording %s' %
                    (str(lbl), str(self.identifier))
                )

        if not as_list:
            if pandas:
                trials, ret_labels = self._label_to_data_pandas(trials, ret_labels)
            else:
                trials, ret_labels = self._label_to_data_numpy(trials, ret_labels)
        return trials, ret_labels

    def get_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                List of Strings
        """
        labels = []
        for t in self._trial_order:
            if self.trials[t].label is not None:
                labels.append(self.trials[t].label)
        return labels

    def get_frequency(self):
        """ Returns frequency of setup used for session this recording was recorded in
        """
        return self._modality.frequency

    @property
    def duration(self):
        """ Returns duartion (sum of duarion of trials) of recording in seconds

            Returns:
                float
        """
        duration = 0
        for trial in self.trials.itervalues():
            duration += trial.duration
        return duration

    @property
    def own_duration(self):
        """ Returns duration of the recording itself.

            Returns:
                float
        """
        return self._data.duration

    @property
    def samples(self):
        """ Returns number of samples (sum of channels of samples) recording
            contains.

            Returns:
                Integer
        """
        return self._samples

    @samples.setter
    def samples(self, num_samples):
        """ Sets number of samples recording holds (samples contained in Trials)

            Args:
                num_samples (int): New number of samples
        """
        self._samples = num_samples

    def set_data(self, data):
        """ Sets only the **relevant** data of the recording, i.e. the data specified
            by the subsequent trials. ''data'' argument is therefore required to have
            the respective dimensionality.

            Args:
                data (pandas.DataFrame): Data to update trials with

            Note:
                This is not a setter be design. If data is set using setter it seems like
                a separate object is created.
                Trials referencing the updated data do net return the new values. When
                accessing data though this classes properties, the updated data is
                returned, though.
        """
        if data.shape[0] != self.samples:
            raise ValueError(
                'Dimension missmatch while trying to set data for recording {}. ' + \
                'Expected data of form ({},{}), instead got {}'.format(
                    self.identifier,
                    self.channels,
                    self.features,
                    data.shape
                )
            )
        else:
            for idnt in self._trial_order:
                start = int(self.trials[idnt].start * self.frequency)
                end = start + int(self.trials[idnt].duration * self.frequency)
                self.trials[idnt].set_data(data[start : end])

    def get_all_data(self):
        """ In contrast to the Data propery, this function will return the whole DataFrame
            having been passed to a Recording object (or read from file).
            The data therein might not represent the original state if operations on the
            data have been performed.

            Returns:
                model.model.DataContainer
        """
        return self._data

    def set_all_data(self, data):
        if (data.shape[0] == self.channels) and (data.shape[1] == self.features):
            self._data = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in recording ' + self.identifier + '. ' +
                '\nExpected shape(' + self.channels + ',' + self.features + ', got ' +
                'shape' + str(data.shape)
            ))

    def get_trial(self, identifier):
        """ Returns the trial specified by identifier.

            Args:
                identifier (string): Identifier of trial

            Returns:
                If successful, trial object

            Raises:
                IndexError: If not trial specified by index exists in recording
        """
        if identifier in self.trials:
            return self.trials[identifier]
        else:
            raise IndexError((
                'Recording %s has no trial with identifier %s' %
                (self.identifier, identifier)
            ))

    def put_trial(self, trial):
        """ Adds a trial to the *trials* object. This method is intended to build up
            the knowledge Base. If no name for the trial is specified, a generic name
            of the form ``trial<number>``, where ``<number>`` is ascending.

            Args:
                trial (Trial): Trial to be added

            Raises:
                IndexError: Raised if trial with duplicate name is added to *trials*
        """
        if trial.identifier not in self.trials:
            self.trials[trial.identifier] = trial
            self._trial_order.append(trial.identifier)
            self.samples = self.samples + trial.samples
        else:
            raise IndexError('Trial with name ' + trial.identifier + ' already member of recording')

    def to_string(self):
        string = (
            'Recording %s: %ds duration, %d samples, %d Trials' %
            (
                self.identifier,
                self.duration,
                self.samples,
                len(self.trials)
            )
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for t in self._trial_order:
            ts = self.trials[t].to_string().replace('\n','\n\t')
            string = string + '\t' + ts + '\n'
        return string


class Trial(DataHoldingElement):
    """ Implements one trial of an EMG experiment. A trial is the smallest amount of data
        to accept or reject a hypothesis.
        A trial belongs to a recording. Consequently the data associated with a trial object
        is a subset of the data of the recording. Given the start and end point (in
        seconds, relative to start of recording) and the setting, i.e. channel frequency,
        this class calculates the indices event start and end.

        Attributes:
            duration (float): Stop point of trial in seconds relative to the stop point of
                the recording.
            identifier (string): Identifier of the trial. For example *bizeps_curl*
            label (String): Class Label
            events (List): List of Event objects
                relative to the start of the trial
            recording (Recording): The recording this trial belongs to. Necessary to
                retrieve informations about the setting.
            samples (int): Number of samples (time steps) Trial contains
            start (float): Start point of trial in seconds relative to the start point
                of the recording.
    """

    def __init__(self, recording, start, duration, identifier=None, label = None):
        """ Initializes Object

            Args:
                recording (Recording): The recording this trial belongs to. Necessary to
                    retrieve informations about the setting.
                start (float): Start point of trial in seconds relative to the start point of
                    the recording (format: ``seconds.miliseconds``).
                duration (float): Stop point of trial in seconds relative to the stop point of
                    the recording (format: ``seconds.miliseconds``).
                identifier (string): Identifier of the trial. For example *bizeps_curl*
                label (String, optional): Class label if existing
        """
        self._recording = recording
        self._start = start
        self._identifier = identifier
        self._duration = duration
        self._label = label
        self._events = []
        self._samples = duration * self._recording.modality.frequency

        if self._identifier is None:
            self._identifier = 'trial' + str(len(self._recording.trials))

        self._recording.put_trial(self)

    @property
    def identifier(self):
        """ Getter Property for identifier attributes

            Returns:
                String
        """
        return self._identifier

    @property
    def recording(self):
        """ Getter Property for recording attribute

            Returns:
                model.model.Recording
        """
        return self._recording

    @property
    def start(self):
        """ Start of Trial relative to beginning of recording in seconds
        """
        return self._start

    @property
    def duration(self):
        """ Duration of Trial in seconds
        """
        return self._duration

    @property
    def label(self):
        """ Getter property for attribute label

            Returns:
                String
        """
        return self._label

    @property
    def samples(self):
        """ Getter property for attribute samples

            Returns:
                int
        """
        return self._samples

    @label.setter
    def label(self, label):
        """ Setter property for attribute label

            Args:
                label (String): Label of trial
        """
        self._label = label

    def add_event(self, name, start, duration=None):
        """ Adds an event to the trial. Position of event is expected to be
            relative to the beginning of the trial

            Args:
                name (string): Name of event
                start (float): Start time relative to beginning of trial in seconds
                duration (float): Duration of event in seconds
        """
        self._events.append(Event(name, start, duration))

    def get_event(self, from_=None, to=None):
        """ Returns all events contained in the given interval. If no interval borders
            are specified, they are set to beginning/end of trial. Thus all events defined
            for trial are returned.

            Args:
                from_ (float, optional): Start from where to retrieve event 
                to (float, optional): End of interval for which events should be retrieved

            Note:
                Returns a copy of the data stored in ``Recording`` and referenced
                by this trial. Changes to the data returned by this function do
                not affect the data stored in ``Recording``.

            Raises:
                IndexError: If either `from_` or `to` exceed duration of trial
        """
        if from_ is None:
            from_ = 0
        elif from_ >= self.duration:
            raise IndexError('Beginning of time interval out of range (greater than duration)')

        if to is None:
            to = self.duration
        elif to > self.duration:
            raise IndexError('End of time interval out of range (greater than duration)')

        ret = []

        for e in self._events:
            if e.start < 0 :
                continue
            elif (e.start > from_) and (t < to):
                # Substract offset of trial
                ret.append(e)
            elif e.start  > self.start + self.duration:
                break
        return ret

    def get_data(self, begin=None, end=None, channels=None):
        """ Returns data within specified interval borders. If no border set start/end
            index of Trial is used respectively.

            Args:
                begin (float): Start point of interval for which to retrieve time.
                    Relative to start point of trial
                end (float): End point of interval for which to retrieve data.
                    Relative to beginning of trial
                channels (List): List of Channel Idenfiers. Only those specified
                    are returned. If none specified all are returned

            Note:
                If channels is specified, columns of returned dataframe/array
                are in the order as channels were listed

            Returns:
                model.model.DataContainer

            Raises:
                IndexError: If either `begin` or `end` larger than duration of trial
        """
        if end is None:
            end = self.start + self.duration
        else:
            end = self.start + end

        if begin is None:
            begin = self.start
        else:
            begin = self.start + begin

        if channels is None:
            container = self.recording.data[begin:end]
        else:
            container = self.recording.data[begin:end, channels]
        return container

    def get_frequency(self):
        """ Returns frequency of recording trial belongs to
        """
        return self.recording.modality.frequency

    def set_data(self, data):
        """ Sets the channels in reference.data this trial is referencing.

            Args:
                data (pandas.DataFrame): New data

            Note:
                This is not a property by purpose. When using a property here, Python seems
                to create a new object behind the scenes and the data object in Record
                class is not changed!
        """
        self.recording.data[self.start:self.start + self.duration] = data

    def to_string(self):
        string = 'Trial {}: {}s duration, {} samples, label {}'.format(
            self.identifier, self.duration, self.samples, self.label
            )
        for e in self._events:
            string = string + '\n\t' + e.to_string()
        return string


class DataController(object):
    """ Handles reading and writing EMG data from file
    """

    def read_data_from_file(self, path):
        """ Given path identifies file type and calls respective method

            Args:
                path (String): Path to file from which data should be retrieved

            Raises:
                IOError if file specified in path does not exist
                NotImplementedError if file type not recognized
        """
        if path.endswith('.txt'):
            return self.read_data_from_file(path)
        elif path.endswith('.pkl'):
            return self.read_pickled_data(path)
        else:
            raise NotImplementedError(
                'File type of file  %s not supported' % path
            )

    def read_data_from_text(self, path, delimiter = '\t', asNumpy = False, debug = False):
        """ Reads EMG data from a textfile

            Args:
                path (String): Path to the text file which should be read
                delimiter (String, optional): Delimiter of columns
                asNumpy (Boolean, optional): If set to true numpy array is returned
                    instead of Pandas DataFrame
                debug (boolean): If set to true only first 100 Lines are considered

            Returns:
                pandas.core.DataFrame
                numpy.ndarray
        """

        with open(path, 'r') as f:
            count = 0
            start = 0
            arr = None
            for line in f:
                count = count + 1

                line = line.strip()

                if re.match('[a-zA-Z]', line) is not None:
                    # Skip all lines containing text characters
                    print 'Warning - skipped line %d:%s' % (count, line)
                    continue

                start = line.index('\t')
                    # Skip the first column. Contains only time values (in case of PowerLab
                    # export
                line = line.replace(',', '.')

                values = line[start + 1: len(line)].split('\t')
                if arr is None:
                    arr = np.array(values, dtype = 'float').reshape(1, len(values))
                else:
                    try:
                        arr = np.row_stack((
                            arr,
                            np.array(values, dtype = 'float').reshape(1, len(values))
                        ))
                    except ValueError as e:
                        print (
                                'Error reading line %i in file %s. Line was %s' %
                                (count, path, line)
                              )
                if (count % 10000) == 0:
                    print '%d lines already read' % count
                if debug:
                    if count > 99:
                        break

        if type(arr) is pd.DataFrame:
            arr = arr.values
        elif type(arr) is np.ndarray:
            pass
        else:
            raise ValueError('Error loading data from pickled file. Encountered ' + \
                    'unsupported data type. Expected pandas.core.DataFrame or ' + \
                    'numpy.ndarray. Instead got {}'.format(type(arr))
                    )

        return arr

    def read_from_file_and_pickle(self, source, target, debug = False):
        """ Reads EMG data from file and creates a numpy array and pickles it to target

            Args:
                source (String): Path to data file
                target (String): Path to pickle file
        """
        arr = self.read_data_from_text(path = source, asNumpy = True, debug = debug)

        with open(target, 'wb') as f:
            pkl.dump(arr, f)

    def read_pickled_data(self, source):
        """ Reads EMG data from a pickled numpy ndarray

            Args
                source (String): Path to pickled numpy.ndarray

            Returns:
                pandas.core.DataFrame
        """
        with open(source, 'rb') as f:
            arr = pkl.load(f)

        if type(arr) is pd.DataFrame:
            arr = arr.values
        elif type(arr) is np.ndarray:
            pass
        else:
            raise ValueError('Error loading data from pickled file. Encountered ' + \
                    'unsupported data type. Expected pandas.core.DataFrame or ' + \
                    'numpy.ndarray. Instead got {}'.format(type(arr))
                    )
        return arr

