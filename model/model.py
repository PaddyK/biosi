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
            >>> recording.getAllData()
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

# TODO: Order keys were added

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

    def getData(self):
        """ Returns all data over all sessions and recordings.
            
            Note:
                The order in which data will be returned is:
                * session1
                    * recording1
                        * trial1
                        * trial2
                    * recording 2
                        * trial1
                        * trial2
                and so forth.

            Returns:
                Dataframe
        """
        df = None
        for s in self.Sessions:
            if df is None:
                df = self.Sessions[s].getData()
            else:
                df = pd.concat([df, self.Sessions[s].getData()])
       
        return df

    def getRecording(self, identifier, session):
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
                    recording = s.getRecording(identifier)
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
                recording = self.Sessions[session].getRecording(identifier)
        return recording
    
    def getTrial(self, identifier, session, recording = None):
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
                    trial = rc.getTrial(identifier)
            if trial is None:
                raise IndexError((
                    'No trial with identifier %s exists in any recording of ' +
                    'session %s' % (identifier, session)
                ))
        else:
            rc = self.getRecording(recording, session) 
                # throws error if recording does not exist.
            trial = rc.getTrial(identifier)

        return trial

    def putSetup(self, setup):
        if setup.Identifier not in self.Setups:
            self.Setups[setup.Identifier] = setup
        else:
            raise IndexError((
                'Setup with identifier ' + setup.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def putSession(self, session):
        if session.Identifier not in self.Sessions:
            self.Sessions[session.Identifier] = session 
            self._session_order.append(session.Identifier)
        else:
            raise IndexError((
                'Session with identifier ' + session.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def putSubject(self, subject):
        if subject.Identifier not in self.Subjects:
            self.Subjects[subject.Identifier] = subject
        else:
            raise IndexError((
                'Subject with identifier ' + subject.Identifier + ' already exists in ' +
                ' experiment'
            ))
    
    def toString(self):
        return (
            'Experiment: %d Setups, %d Sessions, %d Subjects' %
            (len(self.Setups), len(self.Sessions), len(self.Subjects))
        )

    def recursiveToString(self):
        string = self.toString() + '\n'
        string =  string + 'Subjects:\n'
        for s in self.Subjects.itervalues():
            string = string + '\t' + s.toString() + '\n'
        string = string + 'Setups:\n'
        for s in self.Setups.itervalues():
            tmp = s.recursiveToString()
            string = string + '\t' + tmp.replace('\n','\n\t') + '\n'
        string = string + 'Sessions:\n'
        for s in self.Sessions.itervalues():
            tmp = s.recursiveToString()
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

    def toString(self):
        return self.Identifier

class Setup:
    """ Represents a setup for an session. Specifies the used frequency, amount and
        grouping of sensors.
    """

    def __init__(self, experiment, frequency, identifier = None):
        self._frequency = frequency
        self._identifier = identifier
        self._modalities = {}
        self._experiment = experiment
        self._features = 0
        self._modalityOrder = []
 
        if self._identifier is None:
            self._identifier = 'setup' + str(len(self._experiment.Setups))

        self._experiment.putSetup(self)

    @property
    def Frequency(self):
        return self._frequency

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
 
    def getSampleOrder(self):
        order = []
        for idx in self._modalityOrder:
            order.extend(self.Modalities[idx].SampleOrder)
        return order

    def putModality(self, modality):
        if modality.Identifier not in self.Modalities:
            self.Modalities[modality.Identifier] = modality
            self._modalityOrder.append(modality.Identifier)
        else:
            raise IndexError((
                'Modality with identifier ' + modality.Identifier + ' already exists ' +
                'in Setup ' + self.Identifier
            ))
    
    def toString(self):
        return ( 
            'Setup %s: %d Modalities, %d samples/second' %
            (self.Identifier, len(self.Modalities), self.Frequency)
        )
        return string

    def recursiveToString(self):
        string = self.toString() +'\n'
        for m in self.Modalities.itervalues():
            tmp = m.recursiveToString().replace('\n', '\n\t')
            string = string + '\t' + tmp + '\n'
        return string

class Modality:
    """ Represents a modality. A modality in the context of EMG is a group of sensors, for
        example on the hand. Another modality would be a second set of sensors on the breast.
        
        Args:
            setup (Setup): Setup this modality is specified in
            identifier (string, optional): Identifier for this modality. Later usable to
                select a specific instance. If not specified replaced by a generic one

        Attributes
            setup (Setup): Setup this modality is specified in
            identifier (string): Identifier for this modality. Later usable to select one
                specific instanace
            samples (Dictionary): Dictionary of samples i.e. sensors making up modality
    """

    def __init__(self, setup, identifier = None):
        self._setup = setup
        self._identifier = identifier
        self._samples = {}
        self._sampleOrder = []

        if self._identifier is None:
            self._identifier = 'modality' + str(len(self._setup.modalities))
        
        self._setup.putModality(self)

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Samples(self):
        return self._samples

    @property
    def Setup(self):
        return self._setup

    @property
    def SampleOrder(self):
        """ Returns List of identifiers in order in which they were added
            
            returns:
                List of Strings
        """
        return self._sampleOrder

    def putSample(self, sample):
        if sample.Identifier not in self.Samples:
            self.Samples[sample.Identifier] = sample
            self.Setup.Features = self.Setup.Features + 1
            self._sampleOrder.append(sample.Identifier)
        else:
            raise IndexError((
                'Sample with identifier ' + sample.Identifier + ' already exists ' +
                'in Modality ' + self.Identifier
            ))

    def toString(self):
        string = (
            'Modality %s: %d Samples' % (self.Identifier, len(self.Samples))
        )
        return string

    def recursiveToString(self):
        string = self.toString() + '\n'
        for s in self.Samples.itervalues():
            tmp = '\t' + s.toString() + '\n'
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
        
        self._modality.putSample(self)

    @property
    def Identifier(self):
        return self._identifier

    def toString(self):
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

        self._experiment.putSession(self)

    @property
    def Subject(self):
        return self._subject

    @property
    def Setup(self):
        return self._setup

    @property
    def Experiment(self):
        return self._experiment

    @property
    def Recordings(self):
        return self._recordings

    @property
    def Identifier(self):
        return self._identifier

    def getAllData(self):
        """ Returns all data from all recordings belonging to session
            
            Returns:
                pandas.core.DataFrame
        """
        df = None
        for idx in self._recording_order:
            if df is None:
                df = self.Recordings[idx].getAllData()
            else:
                df = pd.concat([df, self.Recordings[idx].getAllData()])
        return df

    def getData(self):
        """ Returns the data of all recordings and trials associated with one Session.
            Only the concatenated data of the trials is returned. Samples not contained
            in trials are skipped.

            Returns:
                pandas.DataFrame
        """
        df = None
        for idx in self._recording_order:
            if df is None:
                df = self.Recordings[idx].getData()
            else:
                df = pd.concat([df, self.Recordings[idx].getData()])
        
        df['sessions'] = self.Identifier
        df.set_index('sessions', inplace = True, append = True)
        df = df.reorder_levels(['sessions', 'recordings', 'trials', 'samples'])
        
        return df
    
    @property
    def Samples(self):
        return self._samples

    def setData(self, data):
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
                self.Recordings[idx].setData(data[offset : end])
                offset = end

    @Samples.setter
    def Samples(self, samples):
        self._samples = samples

    def getRecording(self, identifier):
        if identifier not in self.Recordings:
            raise IndexError(
                'No recording with identifier %s in session %s' %
                (identifier, self.Identifier)
            )
        else:
            return self.Recordings[identifier]

    def putRecording(self, recording):
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

    def putRecordings(self, recordings):
        """ Appends a list of recordings to object attribute *recordings*

            Params:
                recordings (list): List of recordings
        """
        for rc in recordings:
            self.putRecording(rc)

    def toString(self):
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

    def recursiveToString(self):
        string = self.toString() + '\n'
        for r in self.Recordings.itervalues():
            tmp = r.recursiveToString().replace('\n','\n\t')
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

        Note:
            Either ``data`` or ``location`` has to be set. If both are set, ``location``
            is ignored, data is not read from file.

        Attributes:
            session (Session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with samples of this recording.
            duration (int): Duration of recording in data in seconds
            samples (int): Number of samples in this recording. The sum of all sample
                counts of trials being part of this recording
            trials (Dictionary): Trials included in this recording.
            identifier (string): Identifier of one specific instance
            features (int): Number of features in data set
            trial_order (List): Stores order in which trials were added

        Raises:
            ValueError: Raised if both, location and data are not set
    """

    def __init__(self, session, location = None, data = None, identifier = None):
        self._session = session
        self._location = location
        self._data = data
        self._samples = 0
        self._features = self.Session.Setup.Features
        self._trials = {}
        self._identifier = identifier
        self._trial_order = []

        if self._identifier is None:
            self._identifier = 'recording' + str(len(self._session.Recordings))

        if (data is None) and (location is None):
            raise ValueError('Neither location nor data set in Recording')
        
        if data is None:
            # TODO: read from file
            print 'Todo, read data from file'
        self._duration = self._data.shape[0] / self.Session.Setup.Frequency
        self._session.putRecording(self)
    
    @property
    def Session(self):
        return self._session

    @property
    def Location(self):
        return self._location

    @property
    def Trials(self):
        return self._trials
    
    @property
    def Features(self):
        return self._features

    @property
    def Identifier(self):
        return self._identifier

    def getData(self):
        """ Returns the **relevant** data of a recording object. In especially, this
            property yields only the data specified in the trials belonging to the
            recording.
            
            Example:
                Sampling rate of 4000Hz, recording is 60s long. Trial one goes from
                second 10 to second 30, and trial02 from second 35 to second 50.
                Then this function only yields the samples in the intervals 10..30 and
                35..50. So a total of (20 + 15) * 4000 samples instead of 60 * 4000 samples
            
            Returns:
                pandas.DataFrame
        """
        # New data frame is created
        df = None
        for id in self._trial_order:
            if df is None:
                df = self.Trials[id].getData()
            else:
                df = pd.concat([df, self.Trials[id].getData()])
        
        df['recordings'] = self.Identifier
        df.set_index('recordings', append = True, inplace = True)
        # Returns a new object and there is no inplace option
        df = df.reorder_levels(['recordings', 'trials', 'samples'])
        
        return df

    @property
    def Duration(self):
        return self._duration

    @property
    def Samples(self):
        return self._samples
    
    def setData(self, data):
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
            raise ValueError((
                'Dimension missmatch while trying to set data for recording %s. ' +
                'Expected data of form (%s,%s), instead got %s' %
                (
                    str(self.Identifier), 
                    str(self.Samples), 
                    str(self.Features)#,
                    #str(data.shape) 
                )
            ))
        else:
            samples = 0 # Use it as soffset
            for idnt in self._trial_order:
                end = samples + self.Trials[idnt].Samples
                self.Trials[idnt].setData(data[samples : end])
                samples = end
    
    @Samples.setter
    def Samples(self, samples):
        self._samples = samples

    def getAllData(self):
        """ In contrast to the Data propery, this function will return the whole DataFrame
            having been passed to a Recording object (or read from file).
            The data therein might not represent the original state if operations on the
            data have been performed.

            Returns:
                DataFrame
        """
        return self._data

    def setAllData(self, data):
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Features):
            self.Data = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in recording ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
                'shape' + str(data.shape)
            ))

    def getTrial(self, identifier):
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

    def putTrial(self, trial):
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
            raise IndexError('Trial with name ' + name + ' already member of recording')

    def toString(self):
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

    def recursiveToString(self):
        string = self.toString() + '\n'
        for t in self.Trials.itervalues():
            string = string + '\t' + t.toString() + '\n'
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

        Attributes:
            recording (Recording): The recording this trial belongs to. Necessary to
                retrieve informations about the setting.
            start (float): Start point of trial in miliseconds relative to the start point
                of the recording.
            startIdx (int): Offset relative to beginning of recording of trial. Index
                to DataFrame
            stopIdx (int): End of trial relative to recording. Index to DataFrame
            duration (float): Stop point of trial in miliseconds relative to the stop point of
                the recording.
            identifier (string): Identifier of the trial. For example *bizeps_curl*
    """

    def __init__(self, recording, start, duration, identifier):
        self._recording = recording
        self._start = start
        self._duration = duration # Convert to miliseconds
        self._startIdx = 0
        self._stopIdx = 0
        self._identifier = identifier
        self._samples = 0
        
        if self._identifier is None:
            self._name = 'trial' + str(len(self._recording.Trials))
        
        f = self._recording.Session.Setup.Frequency
        self._startIdx = self._start * f
        self._stopIdx = self._startIdx + self._duration * f
        self._samples = self._stopIdx - self._startIdx
        
        self._recording.putTrial(self)

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Recording(self):
        return self._recording

    @property
    def Start(self):
        return self._start

    @property
    def StartIdx(self):
        return self._startIdx

    @property
    def Duration(self):
        return self._duration

    @property
    def StopIdx(self):
        return self._stopIdx 
    
    @property
    def Samples(self):
        return self._samples
    
    def getData(self):
        #idx = pd.MultiIndex.from_product(
        #    [[self.Identifier], np.arange(0, self.Samples)],
        #    names = ['trials', 'samples']
        #)
        tmp = self.Recording.getAllData().iloc[self.StartIdx : self.StopIdx]
        tmp['samples'] = np.arange(self.Samples)
        tmp['trials'] = self.Identifier
        tmp.set_index('trials', inplace = True, append = False)
        tmp.set_index('samples', inplace = True, append = True)
        tmp.columns = self.Recording.Session.Setup.getSampleOrder()        
        return tmp

    def setData(self, data):
        """ Sets the samples in reference.data this trial is referencing.
            
            Args:
                data (pandas.DataFrame): New data

            Note:
                This is not a property by purpose. When using a property here, Python seems
                to create a new object behind the scenes and the data object in Record
                class is not changed!
        """
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Recording.Features):
            self.Recording.getAllData().iloc[self.StartIdx : self.StopIdx] = data.get_values()
        else:
            raise ValueError((
                'Shape missmatch replacing data in trial ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
                'shape' + str(data.shape)
            ))

    def toString(self):
        string = (
            'Trial %s: %fs duration, %d samples' %
            (self.Identifier, self.Duration, self.Samples)
        )
        return string

class DataController:
    """ Handles reading and writing EMG data from file
    """

    def readDataFromText(self, path, delimiter = '\t', asNumpy = False):
        """ Reads EMG data from a textfile
            
            Args:
                path (String): Path to the text file which should be read
                delimiter (String, optional): Delimiter of columns
                asNumpy (Boolean, optional): If set to true numpy array is returned
                    instead of Pandas DataFrame
            
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

                if count < 7:
                    continue

                line = line.strip()
                if re.match('[a-zA-Z]', line) is not None:
                    print 'Warning - skipped line %d:%s' % (count, line)
                    continue

                start = line.index('\t')
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
        if asNumpy:
            ret = arr
        else:
            ret = pd.DataFrame(arr)
        
        return ret

    def readFromFileAndPickle(self, source, target):
        """ Reads EMG data from file and creates a numpy array and pickles it to target
            
            Args:
                source (String): Path to data file
                target (String): Path to pickle file
        """
        arr = self.readDataFromText(source, True)

        with open(target, 'wb') as f:
            pkl.dump(arr, f)
    
    def readPickledData(self, source):
        """ Reads EMG data from a pickled numpy ndarray

            Args
                source (String): Path to pickled numpy.ndarray

            Returns:
                pandas.core.DataFrame
        """
        with open(source, 'rb') as f:
            arr = pkl.load(f)

        return pd.DataFrame(arr)
