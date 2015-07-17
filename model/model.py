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
        Main class.  Contains references to Subject, Session and Subject. This class
        bundles all resources and makes them available to other components

    Subject:
        This class defines a subject participating in an experiment.

    Session:
        This class defines a through setup, subjcet and time defined production of one
        or multiple recordings. Naturally it has a reference to the subjects and setup
        it is defined by and the experiment it belongs to.

    Setup:
        Defines the conditions a session is conducted by. Especially, the different
        groups of sensors employed are defined.
        The class contains a reference to Session and Experiment.

    Subject:
        A subject participating in an experiment by going through one or multiple sessions

    Modality:
        Group(s) of sensors. A modality could for example be all the sensors located
        on the arm and a second one all those on the stomach.

    Sample:
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
import re
import warnings


class Experiment:
    """ Representation of an EMG experiment. This class pools all information to reject
        or accept a hypothesis.

        Attributes:
            setups (Dictionary): Dictionary of Setup objects. Contains all technical
                specification with which EMG measurements were undertaken
            sessions (Dictionary): Dictionary of Session objects. Contains all sessions
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
    def Setups(self):
        return self._setups

    @property
    def Sessions(self):
        return self._sessions

    @property
    def Subjects(self):
        return self._subjects

    def get_data(self, modality, sessions=None, from_=None, to=None):
        """ Returns all data in an specific interval from one/multiple/all
            sessions of this experiment.

            Args:
                modality (String): Identifier of an modality. Only data of recordings
                    with this modality are returned
                sessions (List): List of Strings. If set data for specified recordings
                    are returned, else data of all recordings are returned.
                from_ (float): Start point from which on data should be retrieved
                to (float): End point of data retrieval

            Note:
                `from_` and `to` operate over the accumulated length of specified recordings.
                So if data from all recordings should be selected, but `from_` and `to`
                are very small recordings will be excluded.

            Returns:
                data (pandas.core.DataFrame)
        """
        duration = 0
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

        s_dur = 0
        offset = 0
        to_pass = None
        from_pass = None
        df = None
        for s in sessions:
            offset = offset + s_dur
            s_dur = self.Sessions[s].get_duration(modality=modality)
            if from_ > offset + s_dur:
                # Start point of interval larget than duration of first n recocdings
                # exclude recording and continue
                continue
            elif (from_ > offset) and (from_ < offset + s_dur):
                # If start point of interval lies within nth recording start retrieving
                # from this point. Convert to relative start of recording
                from_pass = from_ - offset
            else:
                from_pass = None

            if to < offset:
                # If accumulated duration of all recordings is larger than end point
                # of time interval stop retrieving data
                break
            elif (to > offset) and (to < offset + s_dur):
                # If end of time interval lies within one recording retrieve only
                # data until relative point of time in recording
                to_pass = to - offset
            else:
                to_pass = None

            tmp = self.Sessions[s].get_data(modality=modality, begin=from_pass, end=to_pass)

            if df is None:
                df = tmp
            else:
                df = pd.concat([df, tmp])

        return df

    def get_data_by_labels(self, labels):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                labels (list): List with class labels

            Returns:
                data (pandas.core.frame.DataFrame)
                labels (List): List with one label per sample in data
        """
        df = None
        retLbls = None
        for idx in self._session_order:
            d, l = self.Sessions[idx].get_data_by_labels(labels)
            if df is None:
                df = d
                retLbls = l
            else:
                df = pd.concat([df, d])

                retLbls = np.concatenate((retLbls, l))

        return df, retLbls

    def get_data_for_breeze(self, labels=None):
        """ Returns data in format to directly feed it to
            .. _Breeze: https://github.com/breze-no-salt/breze/blob/master/docs/source/overview.rst
            That is a list of two dimensional arrays where each array represents a trial.

            Args:
                labels (List): List of strings containing labels of trials (not class labels
                    but identifiers!)
            Returns:
                data (List): List of two dimensional numpy.ndarrays
                lbls (List): List with one dimenional arrays containing class labels
        """

        data = []
        classLabels = []
        for idx in self._session_order:
            dat, clbl = self.Sessions[idx].get_data_for_breeze(labels=labels)
            data.extend(dat)
            classLabels.extend(clbl)

        return data, classLabels

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
            if len(self.Setups) > 1:
                raise ValueError((
                    'More than one Setup defined but none specified. Specify ' +
                    'setup to retrieve frequency'
                ))
            else:
                f = self.Setups[self.Setups.keys()[0]].getFrequency(modality)
        else:
            f = self.Setups[setup].getFrequency(modality)

        return f
        for setup in self.Setups.itervalues():
            if f == 0:
                f = setup.Frequency
            if f != setup.Frequency:
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
            labels.extend(self.Sessions[t].get_labels())

        return labels

    def get_marker(self, modality, sessions=None, from_=None, to=None):
        """ Returns all markers/markers in an specific interval from one/multiple/all
            sessions of this experiment.
            If markers to multiple sessions are returned an offset is added to the time of each
            marker according to the order in which each sessions is listed in `sessions`.
            It is assumed, that data of sessions are retrieved in the same order.

            Args:
                modality (String): Identifier of an modality. Only markers of recordings
                    with this modality are returned
                sessions (List): List of Strings. If set markers for specified recordings
                    are returned, else markers of all recordings are returned.
                from_ (float): Start point from which on markers should be retrieved
                to (float): End point of marker retrieval

            Note:
                `from_` and `to` operate over the accumulated length of specified recordings.
                So if markers from all recordings should be selected, but `from_` and `to`
                are very small recordings will be excluded.

            Returns:
                markers (List): List of tuples containing `time, text` pairs
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
            s_dur = self.Sessions[s].get_duration(modality=modality)
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
                # of time interval stop retrieving markers
                break
            elif (to > offset) and (to < offset + s_dur):
                # If end of time interval lies within one recording retrieve only
                # markers until relative point of time in recording
                to_pass = to - offset

            markers = self.Sessions[s].get_marker(from_=from_pass, to=to_pass)
            for t, l in markers:
                ret.append(((t + offset), l))
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
            for s in self.Sessions.iteritems():
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
            if session not in self.Sessions:
                raise IndexError('Experiment has no session %s', (session))
            else:
                recording = self.Sessions[session].get_recording(identifier)
        return recording

    def get_trial(self, identifier, session, recording = None):
        """ Retrieves a trial

            Args:
                identifier (string): Identifier of the trial (name given)
                session (string): Identifier of the session trial belongs to
                recording (string, optional): Identifier of recording trial belongs to

            Note:
                Session is mandatory, since trials might have duplicate names across
                sessions.

            Returns:
                Trial object if successful

            Raises:
                IndexError: If there does not exist a Session, Recording or Trial with
                Identifier ``session``, ``recording`` or ``trial``
        """
        trial = None
        if session not in self.Sessions:
            raise IndexError('Experiment has no session with identifier %s' % (session))
        elif recoding is None:
            for rc in self.Sessions[session].Recordings.iteritems():
                if identifier in rc.Trials:
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
        if setup.Identifier not in self.Setups:
            self.Setups[setup.Identifier] = setup
        else:
            raise IndexError((
                'Setup with identifier ' + setup.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def put_session(self, session):
        if session.Identifier not in self.Sessions:
            self.Sessions[session.Identifier] = session
            self._session_order.append(session.Identifier)
        else:
            raise IndexError((
                'Session with identifier ' + session.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def put_subject(self, subject):
        if subject.Identifier not in self.Subjects:
            self.Subjects[subject.Identifier] = subject
        else:
            raise IndexError((
                'Subject with identifier ' + subject.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def to_string(self):
        return (
            'Experiment: %d Setups, %d Sessions, %d Subjects' %
            (len(self.Setups), len(self.Sessions), len(self.Subjects))
        )

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        string =  string + 'Subjects:\n'
        for s in self.Subjects.itervalues():
            string = string + '\t' + s.to_string() + '\n'
        string = string + 'Setups:\n'
        for s in self.Setups.itervalues():
            tmp = s.recursive_to_string()
            string = string + '\t' + tmp.replace('\n','\n\t') + '\n'
        string = string + 'Sessions:\n'
        for s in self.Sessions.itervalues():
            tmp = s.recursive_to_string()
            string = string + '\t' + tmp.replace('\n', '\n\t') + '\n'
        return string


class Subject:
    """ Represents subjects having paricipated in the course of an EMG experiment.

        Attributes:
            identifier (string): Identifier of a subject
    """
    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def Identifier(self):
        return self._identifier

    def to_string(self):
        return self.Identifier


class Setup:
    """ Represents a setup for an session. Specifies the amount and
        grouping of sensors of different recording systems.
    """

    def __init__(self, experiment, identifier = None):
        self._identifier = identifier
        self._modalities = {}
        self._experiment = experiment
        self._features = 0
        self._modalityOrder = []

        if self._identifier is None:
            self._identifier = 'setup' + str(len(self._experiment.Setups))

        self._experiment.put_setup(self)

    def getFrequency(self, modality = None):
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
                frequency (int): Frequency (SamplingRate) of a modality
        """

        f = None
        if modality is None:
            if len(self.Modalities) > 1:
                raise ValueError((
                    'More than one modality defined. Specify modality for which' +
                    'to retrieve frequency'
                ))
            else:
                f = self.Modalities[self._modalityOrder[0]].Frequency
        else:
                f = self.Modalities[modality].Frequency

        return f

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Modalities(self):
        return self._modalities

    @property
    def Features(self):
        return self._features

    @Features.setter
    def Features(self, features):
        self._features = features

    def get_sample_order(self):
        order = []
        for idx in self._modalityOrder:
            order.extend(self.Modalities[idx].Sample_Order)
        return order

    def put_modality(self, modality):
        if modality.Identifier not in self.Modalities:
            self.Modalities[modality.Identifier] = modality
            self._modalityOrder.append(modality.Identifier)
        else:
            raise IndexError((
                'Modality with identifier ' + modality.Identifier + ' already exists ' +
                'in Setup ' + self.Identifier
            ))

    def to_string(self):
        return (
            'Setup %s: %d Modalities' %
            (self.Identifier, len(self.Modalities))
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() +'\n'
        for m in self.Modalities.itervalues():
            tmp = m.recursive_to_string().replace('\n', '\n\t')
            string = string + '\t' + tmp + '\n'
        return string


class Modality:
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
            samples (Dictionary): Dictionary of samples i.e. sensors making up modality
            frequency (int): Frequency (Sampling-Rate) at which data points are taken
    """

    def __init__(self, setup, frequency, identifier = None):
        self._setup = setup
        self._identifier = identifier
        self._frequency = frequency
        self._samples = {}
        self._sampleOrder = []

        if self._identifier is None:
            self._identifier = 'modality' + str(len(self._setup.modalities))

        self._setup.put_modality(self)

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Frequency(self):
        return self._frequency

    @property
    def Samples(self):
        return self._samples

    @property
    def Setup(self):
        return self._setup

    @property
    def num_samples(self):
        """ Returns number of defined samples

            Returns:
                int
        """
        return len(self._samples)

    @property
    def Sample_Order(self):
        """ Returns List of identifiers in order in which they were added

            returns:
                List of Strings
        """
        return self._sampleOrder

    def get_sample_index(self, identifier=None):
        """ Returns index of samples specified in ``identifier``

            if ``identifier`` is None values 0..num Samples are returned

            Args:
                identifier (List, String): Either string or list of strings

            Returns:
                indices, List of integers

            Raises:
                ValueError if one of the specified identifier is not found
        """
        if identifier is None:
            return range(len(self.Sample_Order))

        if (type(identifier) == str) or (type(identifier) == unicode):
            identifier = [identifier]

        indices = []
        for id in identifier:
            indices.append(self.Sample_Order.index(id))
        return indices

    def put_sample(self, sample):
        if sample.Identifier not in self.Samples:
            self.Samples[sample.Identifier] = sample
            self.Setup.Features = self.Setup.Features + 1
            self._sampleOrder.append(sample.Identifier)
        else:
            raise IndexError((
                'Sample with identifier ' + sample.Identifier + ' already exists ' +
                'in Modality ' + self.Identifier
            ))

    def to_string(self):
        string = (
            'Modality %s: %d Samples, %d Hz' % (self.Identifier, len(self.Samples), self.Frequency)
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for s in self.Samples.itervalues():
            string = string + '\t' + s.to_string() + '\n'
        return string


class Sample:
    """ Represents a sample i.e. sensor.

        Args:
            modality (Modality): Modality this sample belongs to
            identifier (string, optional): Identifier for this sample. If not set a
                generic one will be used. It is strongly recommended to use a identifier
                here.

        Attributes:
            modality (Modality): Modality this sample belongs to
            identifier (string): Identifier for this sample
    """

    def __init__(self, modality, identifier = None):
        self._modality = modality
        self._identifier = identifier

        if self._identifier is None:
            self._identifier = 'sample' + str(len(self._modality.Samples))

        self._modality.put_sample(self)

    @property
    def Identifier(self):
        return self._identifier

    def to_string(self):
        return 'Sample: ' + self.Identifier


class Session:
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
            self._identifier = 'session' + str(len(self._experiment.Sessions))

        self._experiment.put_session(self)

    @property
    def Subject(self):
        """ Returns subject object associated with session

            Returns:
                model.model.Subject
        """
        return self._subject

    @property
    def Setup(self):
        """ Returns setup associated with session

            Returns:
                model.model.Session
        """
        return self._setup

    @property
    def Experiment(self):
        """ Returns experiment session belongs to

            Returns:
                model.model.Experiment
        """
        return self._experiment

    @property
    def Recordings(self):
        """ Returns recordings for this session

            Returns:
                Dictionary of model.model.Recording
        """
        return self._recordings

    @property
    def Identifier(self):
        """ Returns identifier of this session

            Returns:
                String
        """
        return self._identifier

    def get_all_data(self):
        """ Returns all data from all recordings belonging to session

            Returns:
                pandas.core.DataFrame
        """
        df = None
        for idx in self._recording_order:
            if df is None:
                df = self.Recordings[idx].get_all_data()
            else:
                df = pd.concat([df, self.Recordings[idx].get_all_data()])
        return df

    def get_data_by_labels(self, labels):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                labels (list): List with class labels

            Returns:
                data (pandas.core.frame.DataFrame)
                labels (numpyp.ndarray): Array with one label per sample in data
        """
        df = None
        retLbls = None
        for idx in self._recording_order:
            d, l = self.Recordings[idx].get_data_by_labels(labels)
            if df is None:
                df = d
                retLbls = l
            else:
                df = pd.concat([df, d])
                retLbls = np.concatenate((retLbls, l))

        return df, retLbls

    def get_duration(self, modality=None):
        """ Returns session's duration depending on recordings associated with
            `modality`. If `modality` is not set, all recordings of session are
            considered

            Args:
                modality (String): Identifier of a modality

            Returns:
                duration (float): Sum of duration of all recordings as duration of session
        """
        duration = 0
        for r in self.Recordings.itervalues():
            if modality is None:
                duration = duration + r.Duration
            elif r.Modality == modality:
                duration = duration + r.Duration
        return duration

    def get_data_for_breeze(self, labels=None):
        """ Returns data in format to directly feed it to
            .. _Breeze: https://github.com/breze-no-salt/breze/blob/master/docs/source/overview.rst
            That is a list of two dimensional arrays where each array represents a trial.

            Returns:
                data (List): List of two dimensional numpy.ndarrays
                lbls (List): List with one dimenional arrays containing class labels
        """

        data = []
        classLabels = []
        for idx in self._recording_order:
            dat, clbl = self.Recordings[idx].get_data_for_breeze(labels=labels)
            data.extend(dat)
            classLabels.extend(clbl)

        return data, classLabels

    def get_data(self, modality=None, begin=None, end=None):
        """ Returns the data of all recordings and trials associated with one Session.
            Only the concatenated data of the trials is returned. Samples not contained
            in trials are skipped.
            If `begin` and `end` are specified only data of this time interval is
            returned from recording.
            For modality set (being required for more than one modality in setup) only
            data of recordings with this modality are returned

            Args:
                modality (string): Identifier of an modality. Required for more than one
                    modality present in session's setup.
                begin (float): Start point of time interval in seconds
                end (float): End point of time interval in seconds

            Note:
                `begin` and `end` operate on all recordints (with `modality`)
                concatenated in the order in which they were added during experiment
                setup.

            Returns:
                pandas.DataFrame
        """
        if (len(self.Setup.Modalities) > 1) and (modality is None):
            raise ValueError((
                'More than one modality present in setup {a} of session ' +
                '{s} but modality argument was not defined'
                ).format(a=self.Setup.Identifier, s=self.Identifier)
            )

        df = None
        begin_pass = None
        end_pass = None
        stop = 0

        for idx in self._recording_order:
            if (self.Recordings[idx].Modality == modality) or (modality is None):
                offset = stop # Offset has to be set here to ensure its set
                              # even if continue clause is executed!
                stop = self.Recordings[idx].Duration + offset

                if begin is not None:
                    if begin > stop:
                        # Skip all Recordings for which end point of recording is smaler
                        # than start point of interval. i.e. are not contained in interval
                        continue
                    elif (begin < stop) and (begin > offset):
                        begin_pass = begin - offset
                    else:
                        begin_pass = None

                if end is not None:
                    if end < offset:
                        # If endpoint of time interval is smaller than beginning of new
                        # interval stop retrieving data
                        break
                    elif (end > offset) and (end < stop):
                        end_pass = end - offset
                    else:
                        end_pass = None

                tmp = self.Recordings[idx].get_data(begin=begin_pass, end=end_pass)

                if df is None:
                    df = tmp
                else:
                    df = pd.concat([df, tmp])

        df['sessions'] = self.Identifier
        df.set_index('sessions', inplace = True, append = True)
        df = df.reorder_levels(['sessions', 'recordings', 'trials', 'samples'])

        return df

    def get_frequency(self, modality):
        """ Returns Frequency of setup

            Args:
                Modality for which frequency is going to be retrieved
        """
        return self.Setup.getFrequency(modality=modality)

    def get_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                List of Strings
        """
        labels = []
        for t in self._recording_order:
            labels.extend(self.Recordings[t].get_labels())

        return labels

    def get_marker(self, recordings=None, from_=None, to=None):
        """ Returns all markers/markers in an specific interval from one/multiple/all
            recordings of this session.
            If multiple recordings are returned an offset is added to the time of each
            marker according to the order in which each recording is listed in `recordings`.
            It is assumed, that data of recordings are retrieved in the same order.

            Args:
                recordings (List): List of Strings. If set markers for specified recordings
                    are returned, else markers of all recordings are returned.
                from_ (float): Start point from which on markers should be retrieved
                to (float): End point of marker retrieval

            Note:
                `from_` and `to` operate over the accumulated length of specified recordings.
                So if markers from all recordings should be selected, but `from_` and `to`
                are very small recordings will be excluded.

            Returns:
                markers (List): List of tuples containing `time, text` pairs
        """
        duration = 0
        if recordings is None:
            recordings = self._recording_order

        for rec in recordings:
            if rec in self._recording_order:
                duration = duration + self.Recordings[rec].Duration
            else:
                raise IndexError(
                    'No recording with identifier %s in Session %s' %
                    (rec, self.Identifier)
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
            rec_dur = self.Recordings[rec].Duration
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
                # of time interval stop retrieving markers
                break
            elif (to > offset) and (to < offset + rec_dur):
                # If end of time interval lies within one recording retrieve only
                # markers until relative point of time in recording
                to_pass = to - offset

            markers = self.Recordings[rec].get_marker(from_=from_pass, to=to_pass)

            for t, l in markers:
                ret.append(((t + offset), l))

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
            if modality == self.Recordings[rid].Modality:
                ret.append(self.Recordings[rid])

        if len(ret) == 0:
            warnings.warn('No recording found recorded with modality %s' % modality)

        return ret
    @property
    def Samples(self):
        return self._samples

    def set_data(self, data):
       """ Sets the data of all trials in all recordings belonging to this session.

            Args:
                data (pandas.DataFrame): New data for session

            Raises:
                ValueError: Raised if number of samples/features does not match
        """

       if (data.shape[0] != self.Samples) or (data.shape[1] != self.Setup.Features):
            raise ValueError((
                'Input has wrong dimensions for session %s. Expected data of ' +
                'dimensionality (%s,%s), instead got (%s, %s)' %
                (
                    self.Identifier,
                    self.Samples,
                    self.Setup.Features,
                    data.shape[0],
                    data.shape[1]
                )
            ))
       else:
            offset = 0
            for idx in self._recording_order:
                end = self.Recordings[idx].Samples + offset
                self.Recordings[idx].set_data(data[offset : end])
                offset = end

    @Samples.setter
    def Samples(self, samples):
        self._samples = samples

    def get_recording(self, identifier):
        if identifier not in self.Recordings:
            raise IndexError(
                'No recording with identifier %s in session %s' %
                (identifier, self.Identifier)
            )
        else:
            return self.Recordings[identifier]

    def put_recording(self, recording):
        """ Appends one recording to object attribute *recordings*

            Params:
                recording (Recording): Recording to associate with session
        """
        if recording.Identifier not in self.Recordings:
            self.Recordings[recording.Identifier] = recording
            self._recording_order.append(recording.Identifier)
        else:
            raise IndexError((
                'Recording with identifier ' + recording.Identifier + ' already exists' +
                ' in session ' + self.Identifier
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
            'Session %s: Subject %s, Setting %s, %d recordings' %
            (
                self.Identifier,
                self.Subject.Identifier,
                self.Setup.Identifier,
                len(self.Recordings)
            )
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for r in self.Recordings.itervalues():
            tmp = r.recursive_to_string().replace('\n','\n\t')
            string = string + '\t' + tmp + '\n'
        return string


class Recording:
    """ Represents one recording of a session. May contain multiply trials, i.e. performed
        tasks.

        Args:
            session (Session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with samples of this recording.
            identifier (string, optional): Identifier of one instance
            modality (String, optional): Modality recording is associated with. Set if
                multiple modalities (e.g. eeg, emg) are used

        Note:
            Either ``data`` or ``location`` has to be set. If both are set, ``location``
            is ignored, data is not read from file.

        Attributes:
            session (Session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with samples of this recording.
            duration (float): Duration of recording in data in seconds
            samples (int): Number of samples in this recording. The sum of all sample
                counts of trials being part of this recording
            trials (Dictionary): Trials included in this recording.
            identifier (string): Identifier of one specific instance
            features (int): Number of features in data set
            trial_order (List): Stores order in which trials were added
            modality (String): Modality recording is associated with
            markers (List): Sorted list of tuples. First element of tuple is time of marker
                in seconds. Second element is label. List is sorted after time

        Raises:
            ValueError: Raised if both, location and data are not set
    """

    def __init__(self, session, modality, location = None, data = None,
            identifier = None):
        self._session = session
        self._location = location
        self._samples = 0
        self._features = self.Session.Setup.Modalities[modality].num_samples
        self._trials = {}
        self._identifier = identifier
        self._trial_order = []
        self._modality = modality
        self._markers = []

        if self._identifier is None:
            self._identifier = 'recording' + str(len(self._session.Recordings))

        if (data is None) and (location is None):
            raise ValueError('Neither location nor data set in Recording')

        if data is None:
            datactrl = DataController()
            self._data = datactrl.read_data_from_file(location)
        else:
            if type(data) is pd.DataFrame:
                self._data = data.values
            elif type(data) is np.ndarray:
                self._data = data
            else:
                raise ValueError('Data is of unsupported type. Expected ' + \
                        '"numpy.ndarray or pandas.core.DataFrame. Got {}'
                        .format(type(data))
                        )
        self._duration = self._data.shape[0] / self.Session.Setup.getFrequency(
                self._modality
                )
        self._session.put_recording(self)

    @property
    def Session(self):
        """ Returns session recording belongs to

            Returns:
                model.model.Session
        """
        return self._session

    @property
    def Location(self):
        """ Returns path to file data for recording is stored

            Returns:
                String
        """
        return self._location

    @property
    def Trials(self):
        """ Returns Trials defined for Recording

            Returns:
                model.model.Trial
        """
        return self._trials

    @property
    def Features(self):
        """ Return number of features

            Returns:
                int
        """
        return self._features

    @property
    def Identifier(self):
        """ Returns identifier of this recording

            Returns:
                String
        """
        return self._identifier

    @property
    def Modality(self):
        """ Returns Modality associated with this recording

            Returns:
                model.model.Modality
        """
        return self._modality

    def add_marker(self, marker):
        """ Adds a tuple (time, text) to list of recordings markers

            Args:
                marker (Tuple): Mark to add. Must have form `(time, text)` where `time` is
                    point of time in seconds relative to start of recording where mark
                    should be set and `text` the label of the mark
        """
        time, label = marker
        if len(self._markers) == 0:
            self._markers.append(marker)
        else:
            max = self._markers[len(self._markers) - 1][0]
            if time >= max:
                self._markers.append(marker)
            else:
                for i in range(len(self._markers) - 1, -1, -1):
                    t = self._markers[i][0]
                    if time > t:
                        # Must be inserted after that element
                        self._markers.insert(i + 1, marker)
                        break

    def get_marker(self, from_=None, to=None):
        """ Returns markers either for whole recording or for a specific time interval

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
                from_ (float, optional): Start of time interval for which marks should be retrieved
                to (float, optional): End of time interval for which marks should be retrieved

            Note:
                If either `from` or `to` is set alone, all markers from `start` until
                end of recording or all markers from beginning of recording until `to`
                are returned.

            Raises:
                IndexError: If either `_from` or `to` is higher than recording's duration
        """
        if from_ is None:
            from_ = 0
        elif from_ >= self.Duration:
            raise IndexError('Start point of interval higher than duration of recording')

        if to is None:
            to = self.Duration
        elif to > self.Duration:
            raise IndexError('End point of interval higher than duration of recording')

        duration = 0
        offset = 0
        to_pass = None
        from_pass = None
        ret = []
        for trial in self._trial_order:
            offset = offset + duration
            duration = self.Trials[trial].Duration

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

            tmp = self.Trials[trial].get_marker(from_=from_pass, to=to_pass)
            for t, l in tmp:
                ret.append((t + offset, l))

        return ret

    def get_all_marker(self):
        """ Returns all markers defined for this recording

            Returns:
                List of (float, String) tuples
        """
        return self._markers

    def get_data(self, begin=None, end=None, pandas=True):
        """ Returns the **relevant** data of a recording object. In especially, this
            property yields only the data specified in the trials belonging to the
            recording.
            If `begin` and `end` are specified onlyt data contained in time interval is
            returned.

            Args:
                begin (float): Point of time in seconds of beginning of time interval
                end (float): Point of time in seconds of ending of time interval
                pandas (boolean): Whether or not to return as pandas.core.DataFrame

            Example:
                Sampling rate of 4000Hz, recording is 60s long. Trial one goes from
                second 10 to second 30, and trial02 from second 35 to second 50.
                Then this function only yields the samples in the intervals 10..30 and
                35..50. So a total of (20 + 15) * 4000 samples instead of 60 * 4000 samples

            Returns:
                pandas.DataFrame
        """
        if begin > end:
            raise ValueError((
                'Beginning of time interval larger than ending. Beginning was {beg},' +
                'end was {e}'
                ).format(beg=begin, e=end)
            )
        elif begin >= self.Duration:
            raise ValueError((
                'Beginning of time interval larger than duration of recording {rec}. ' +
                'Start point of interval was at {a}s, duration is {b}s'
                ).format(a=begin, b=self.Duration)
            )
        elif end > self.Duration:
            raise ValueError((
                'End of time interval larger than duration of recording {rec}. ' +
                'Start point of interval was at {a}s, duration is {b}s'
                ).format(a=end, b=self.Duration)
            )
        # New data frame is created
        df = None
        begin_pass = None
        end_pass = None
        stop = 0

        for idx in self._trial_order:
            offset = stop # Offset has to be set here to ensure its set
                          # even if continue clause is executed!
            stop = offset + self.Trials[idx].Duration

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

            tmp = self.Trials[idx].get_data(begin=begin_pass, end=end_pass)
            if df is None:
                df = tmp
            elif pandas:
                df = pd.concat([df, tmp])
            else:
                df = np.row_stack([df, tmp])

        if pandas:
            df['recordings'] = self.Identifier
            df.set_index('recordings', append = True, inplace = True)
            # Returns a new object and there is no inplace option
            df = df.reorder_levels(['recordings', 'trials', 'samples'])
        return df

    def get_data_by_labels(self, labels):
        """ Returns data of all trials with the labels specified in ''labels''.
            Returned DataFrame does not have an MultiIndex

            Args:
                labels (list): List with class labels

            Returns:
                data (pandas.core.frame.DataFrame)
                labels (numpy.ndarray): Array  with one label per sample in data
        """
        df = None
        retLbls = None
        for idx in self._trial_order:
            if self.Trials[idx].Label in labels:
                if df is None:
                    df = self.Trials[idx].get_data()
                    retLbls = np.repeat(self.Trials[idx].Label, df.shape[0])
                else:
                    tmp = self.Trials[idx].get_data()
                    df = pd.concat([df, tmp])
                    retLbls = np.concatenate((
                        retLbls,
                        np.repeat(self.Trials[idx].Label, tmp.shape[0])
                    ))

        for lbl in labels:
            if lbl not in retLbls:
                warnings.warn(
                    'Label %s was not found in any trial of recording %s' %
                    (str(lbl), str(self.Identifier))
                )
        return df, retLbls

    def get_trials_as_list(self, pandas=True, samples=None):
        """ Returns data in format to directly feed it to
            .. _Breeze: https://github.com/breze-no-salt/breze/blob/master/docs/source/overview.rst
            That is a list of two dimensional arrays where each array represents a trial.

            Args:
                pandas (Boolean, optional): True return dataframe, false array
                samples (List): List of sample ids. If set only those samples
                    are returned
            
            Raises:
                KeyError one of identifiers in samples not found

            Returns:
                data (List): List of two dimensional numpy.ndarrays
        """
        data = []
        for idx in self._trial_order:
            tmp = self.Trials[idx].get_data(pandas=pandas, samples=samples)
            data.append(tmp)

        return data

    def get_labels(self):
        """ Returns a list of labels for all relevant data points.

            Returns:
                List of Strings
        """
        labels = []
        for t in self._trial_order:
            labels.extend(self.Trials[t].get_labels())

        return labels

    def get_frequency(self):
        """ Returns frequency of setup used for session this recording was recorded in
        """
        return self.Session.get_frequency(modality = self._modality)

    @property
    def Duration(self):
        """ Returns duartion (sum of duarion of trials) of recording in seconds

            Returns:
                float
        """
        return self._duration

    @property
    def Samples(self):
        """ Returns number of samples (sum of samples of trials) recording
            contains.

            Returns:
                Integer
        """
        return self._samples

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
        if (data.shape[0] != self.Samples) or (data.shape[1] != self.Features):
            raise ValueError(
                'Dimension missmatch while trying to set data for recording {}. ' + \
                'Expected data of form ({},{}), instead got {}'.format(
                    self.Identifier,
                    self.Samples,
                    self.Features,
                    data.shape
                )
            )
        else:
            samples = 0 # Use it as soffset
            for idnt in self._trial_order:
                end = samples + self.Trials[idnt].Samples
                self.Trials[idnt].set_data(data[samples : end])
                samples = end

    @Samples.setter
    def Samples(self, samples):
        self._samples = samples

    def get_all_data(self):
        """ In contrast to the Data propery, this function will return the whole DataFrame
            having been passed to a Recording object (or read from file).
            The data therein might not represent the original state if operations on the
            data have been performed.

            Returns:
                DataFrame
        """
        return self._data

    def set_all_data(self, data):
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Features):
            self.Data = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in recording ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
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
        if identifier in self.Trials:
            return self.Trials[identifier]
        else:
            raise IndexError((
                'Recording %s has no trial with identifier %s' %
                (self.Identifier, identifier)
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
        if trial.Identifier not in self.Trials:
            self.Trials[trial.Identifier] = trial
            self._trial_order.append(trial.Identifier)
            self.Samples = self.Samples + trial.Samples
            self.Session.Samples = self.Session.Samples + trial.Samples
        else:
            raise IndexError('Trial with name ' + trial.Identifier + ' already member of recording')

    def to_string(self):
        string = (
            'Recording %s: %ds duration, %d samples, %d Trials' %
            (
                self.Identifier,
                self.Duration,
                self.Samples,
                len(self.Trials)
            )
        )
        return string

    def recursive_to_string(self):
        string = self.to_string() + '\n'
        for t in self._trial_order:
            ts = self.Trials[t].to_string().replace('\n','\n\t')
            string = string + '\t' + ts + '\n'
        return string


class Trial:
    """ Implements one trial of an EMG experiment. A trial is the smallest amount of data
        to accept or reject a hypothesis.
        A trial belongs to a recording. Consequently the data associated with a trial object
        is a subset of the data of the recording. Given the start and end point (in
        seconds, relative to start of recording) and the setting, i.e. sample frequency,
        this class calculates the indices marking start and end.

        Args:
            recording (Recording): The recording this trial belongs to. Necessary to
                retrieve informations about the setting.
            start (float): Start point of trial in seconds relative to the start point of
                the recording (format: ``seconds.miliseconds``).
            duration (float): Stop point of trial in seconds relative to the stop point of
                the recording (format: ``seconds.miliseconds``).
            identifier (string): Identifier of the trial. For example *bizeps_curl*
            label (String, optional): Class label if existing

        Attributes:
            recording (Recording): The recording this trial belongs to. Necessary to
                retrieve informations about the setting.
            start (float): Start point of trial in seconds relative to the start point
                of the recording.
            startIdx (int): Offset relative to beginning of recording of trial. Index
                to DataFrame
            stopIdx (int): End of trial relative to recording. Index to DataFrame
            duration (float): Stop point of trial in seconds relative to the stop point of
                the recording.
            identifier (string): Identifier of the trial. For example *bizeps_curl*
            marker (List): List of (time, string) tuples specifying some event
                relative to the start of the trial
    """

    def __init__(self, recording, start, duration, identifier, label = None):
        self._recording = recording
        self._start = start
        self._duration = duration
        self._startIdx = 0
        self._stopIdx = 0
        self._identifier = identifier
        self._samples = 0
        self._label = label
        self._marker = []

        if self._identifier is None:
            self._name = 'trial' + str(len(self._recording.Trials))

        f = self._recording.get_frequency()
        self._startIdx = int(self._start * f)
        self._stopIdx = int(self._startIdx + self._duration * f)
        self._samples = self._stopIdx - self._startIdx

        self._recording.put_trial(self)

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Recording(self):
        return self._recording

    @property
    def Start(self):
        """ Start of Trial relative to beginning of recording in seconds
        """
        return self._start

    @property
    def StartIdx(self):
        return self._startIdx

    @property
    def Duration(self):
        """ Duration of Trial in seconds
        """
        return self._duration

    @property
    def Label(self):
        return self._label

    @property
    def StopIdx(self):
        return self._stopIdx

    @property
    def Samples(self):
        return self._samples

    @Label.setter
    def Label(self, label):
        self._label = label

    def add_marker(self, marker):
        """ Adds a merker to the trial. Position of marker is expected to be
            relative to the beginning of the trial

            Args:
                marker (Tuple): Tuple specifying position of marker in seconds and label
                    of marker: `(time, label)`. `time` is relative to the beginning of
                    the trial
        """
        time, label = marker
        time = time + self.Start
        self.Recording.add_marker((time, label))
        self._marker.append(marker)

    def get_marker(self, from_=None, to=None):
        """ Returns all markers contained in the given interval. If no interval borders
            are specified, they are set to beginning/end of trial. Thus all markers defined
            for trial are returned.

            Args:
                from_ (float, optional): Start from where to retrieve markers
                to (float, optional): End of interval for which markers should be retrieved

            Note:
                Returns a copy of the data stored in ``Recording`` and referenced
                by this trial. Changes to the data returned by this function do
                not affect the data stored in ``Recording``.

            Raises:
                IndexError: If either `from_` or `to` exceed duration of trial
        """
        if from_ is None:
            from_ = 0
        elif from_ >= self.Duration:
            raise IndexError('Beginning of time interval out of range (greater than duration)')

        if to is None:
            to = self.Duration
        elif to > self.Duration:
            raise IndexError('End of time interval out of range (greater than duration)')

        #from_ = from_ + self.Start
        #to = to + self.Start
        ret = []
        #markers = self.Recording.get_all_marker()
        ## TODO: Use binary search to find start of range

        for t, l in self._marker:
        #    t = t - self.Start
            if t < 0 :
                continue
            elif (t > from_) and (t < to):
                # Substract offset of trial
                ret.append((t, l))
            elif t > self.Start + self.Duration:
                break
        return ret

    def get_data(self, begin=None, end=None, pandas=True, samples=None):
        """ Returns data within specified interval borders. If no border set start/end
            index of Trial is used respectively.

            Args:
                begin (float): Start point of interval for which to retrieve time.
                    Relative to start point of trial
                end (float): End point of interval for which to retrieve data.
                    Relative to beginning of trial
                pandas (Boolean): Returning data as pandas.core.DataFrame (``True``)
                samples (List): List of Sample Idenfiers. Only those specified
                    are returned. If none specified all are returned

            Note:
                If samples is specified, columns of returned dataframe/array
                are in the order as samples were listed

            Returns:
                data (pandas.core.DataFrame)
                data (numpy.ndarray)

            Raises:
                IndexError: If either `begin` or `end` larger than duration of trial
        """
        if begin is None:
            begin = self.StartIdx
        elif begin >= self.Start + self.Duration:
            raise IndexError((
                'Beginning of time interval out of range. Start point of data retrieval ' +
                ' was {start} but Trial {trial} only of length {length}'
                ).format(start=begin, trial=self.Identifier, length=self.Identifieri)
            )
        else:
            begin = begin * self.Recording.get_frequency() + self.StartIdx

        if end is None:
            end = self.StopIdx
        elif end > self.Duration:
            raise IndexError((
                'End of time interval out of range. Start point of data retrieval ' +
                ' was {start} but Trial {trial} only of length {length}'
                ).format(start=end, trial=self.Identifier, length=self.Identifieri)
            )
        else:
            end = end * self.Recording.get_frequency() + self.StartIdx

        sample_indices = self.Recording.Session.Setup.Modalities[
                self.Recording.Modality].get_sample_index(identifier=samples)

        tmp = None
        begin = int(begin)
        end = int(end)
        if pandas:
            tmp = pd.DataFrame(
                    self.Recording.get_all_data()[begin:end, sample_indices]
                    )
            tmp['samples'] = np.arange(tmp.shape[0])
            tmp['trials'] = self.Identifier
            tmp.set_index('trials', inplace = True, append = False)
            tmp.set_index('samples', inplace = True, append = True)

            if samples is None:
                tmp.columns = self.Recording.Session.Setup.Modalities[
                        self.Recording.Modality
                        ].Sample_Order
            else:
                tmp.columns = samples
        else:
            tmp = np.copy(self.Recording.get_all_data()[begin:end, sample_indices])
        return tmp

    def get_frequency(self):
        """ Returns frequency of recording trial belongs to
        """
        return self.Recording.get_frequency()

    def set_data(self, data):
        """ Sets the samples in reference.data this trial is referencing.

            Args:
                data (pandas.DataFrame): New data

            Note:
                This is not a property by purpose. When using a property here, Python seems
                to create a new object behind the scenes and the data object in Record
                class is not changed!
        """
        if type(data) == pd.core.frame.DataFrame:
            data = data.values()
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Recording.Features):
            self.Recording.get_all_data()[self.StartIdx : self.StopIdx] = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in trial ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
                'shape' + str(data.shape)
            ))

    def to_string(self):
        string = (
            'Trial %s: %fs duration, %d samples' %
            (self.Identifier, self.Duration, self.Samples)
        )
        marker = self.get_marker()
        for t, l in marker:
            string = string + '\n\tMarker {a} at {b:.3f}s'.format(a=l, b=t)
        return string


class DataController:
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
