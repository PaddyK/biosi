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
"""

from abc import ABCMeta
import ConfigParser
import configparser

class Experiment:
    """
    """

    def __init__(self):
        #  TODO: implement this for real
        self._setups = None
        self._sessions = None
        self._subjects = None

    def createFromConfig(self, configFile):
        parser = ConfigParser.ConfigParser()
        parser._interpolate = configparser.ExtendedInterpolation()
        parser.read(configFile)

    @property
    def Setups(self):
        # TODO: implement method stub
        return self._setups

    @property
    def Sessions(self):
        # TODO: implement method stub
        return self._sessions

    @property
    def Subjects(self):
        # TODO: implement method stub
        return self._subjects

    def getSession(self, identifier):
        # TODO: implement method stub
        return None

    def getSubject(self, identifier):
        # TODO: implement method stub
        return None

    def getSetup(self, identifier):
        # TODO: implement method stub
        return None

    def getTrialsBySession(self, session):
        # TODO: impelment method sutb
        return None

    def getTrialsByRecording(self, recording):
        # TODO: impelment method sutb
        return None

    def getRecordings(self, session):
        # TODO: impelment method sutb
        return None

    def getModalities(self, setup):
        # TODO: impelment method sutb
        return None

    def getSampleByModality(self, modality):
        # TODO: impelment method sutb
        return None

    @Setups.setter
    def Setups(self, setups):
        self._setups = setups

    @Sessions.setter
    def Sessions(self, sessions):
        self._sessions = sessions

    @Subjects.setter
    def Subjects(self, subjects):
        self._subjects = subjects

    def putSetup(self, setup):
        if setup.Identifier not in self.Setups:
            self.Setups[setup.Identifier] = setup
        else:
            raise IndexError((
                'Setup with identifier ' + setup.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def putSession(self, session):
        if session.Identifier not in self.Session:
            self.Sessions[session.Identifier] = session 
        else:
            raise IndexError((
                'Session with identifier ' + session.Identifier + ' already exists in ' +
                ' experiment'
            ))

    def putSubject(self, subject):
        if subject.Identifier not in self.Subjects:
            self.Setups[subject.Identifier] = subject
        else:
            raise IndexError((
                'Subject with identifier ' + subject.Identifier + ' already exists in ' +
                ' experiment'
            ))

class Subject:

    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def Identifier(self):
        return self._identifier

class Setup:
    """ Represents a setup for an session. Specifies the used frequency, amount and
        grouping of sensors.
    """

    def __init__(self, experiment, frequency, identifier = None):
        self._frequency = frequency
        self._identifier = identifier
        self._modalities = {}
        self._experiment = experiment

        if self._identifier is None:
            self._identifier = 'setup' + str(len(self._experiment.sessions))

        self._experiment.addSetup(self)

    @property
    def Frequency(self):
        return __frequency

    @property
    def Identifier(self):
        return self._identifier

    @property
    def Modalities(self):
        return self._modalities

    def putModality(self, modality):
        if modality.Identifier not in self.Modalities:
            self.Modalities[modality.Identifier] = modality
        else:
            raise IndexError((
                'Modality with identifier ' + modality.Identifier + ' already exists ' +
                'in Setup ' + self.Identifier
            ))

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

        if self._identifier is None:
            self._identifier = 'modality' + str(len(self._setup.modalities))

        @property
        def Identifier(self):
            return self._identifier

        @property
        def Samples(self):
            return self._samples

        def putSample(self, sample):
            if sample.Identifier not in self.Samples:
                self.Samples[sample.Identifier] = sample
            else:
                raise IndexError((
                    'Sample with identifier ' + sample.Identifier + ' already exists ' +
                    'in Modality ' + self.Identifier
                ))

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
    """

    def __init__(self, experiment, setup, subject, identifier):
        self._identifier = identifier
        self._subject = subject
        self._setup = setup
        self._experiment = experiment
        self._recordings = {}
        
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

    @Subject.setter
    def Subject(self, subject):
        self._subject = subject

    @Setup.setter
    def Setup(self, setup):
        self._setup = setup

    @Recordings.setter
    def Recordings(self, recordings):
        self._recordings = recordings

    def putRecording(self, recording):
        """ Appends one recording to object attribute *recordings*

            Params:
                recording (Recording): Recording to associate with session
        """
        if recording.Identifier not in self.Recordings:
            self.Recordings[recording.Identifier] = recording
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

class Recording:
    """ Represents one recording of a session. May contain multiply trials, i.e. performed
        tasks.

        Args:
            session (Session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with samples of this recording.
                If this attribute is set, ``start`` and ``stop`` attributes need also
                be set.
            start (int): Start Index of recording in data
            stop (int): Stop index of recording in data
            identifier (string, optional): Identifier of one instance

        Note:
            Either ``data`` or ``location`` has to be set. If both are set, ``location``
            is ignored, data is not read from file.

        Attributes:
            session (Session): The session in which recording was recorded
            location (string, optional): Path to a file containing the record. If this
                parameter is set and no data is given, data will be retrieved from file.
            data (pandas.DataFrame, optional): DataFrame with samples of this recording.
            start (int): Start Index of recording in data
            stop (int): Stop index of recording in data
            duration (float): Duration of the recording in seconds. Calculated using
                frequency specified in the for the session used setup.
            samples (int): Number of samples in this recording.
            trials (Dictionary): Trials included in this recording.
            identifier (string): Identifier of one specific instance
            features (int): Number of features in data set

        Raises:
            ValueError: Raised if both, location and data are not set or if data is set,
                but either start or stop (or both) are not
    """

    def __init__(self, session, location = None, data = None, start = None, stop = None,
            identifier = None):
        self._session = session
        self._location = location
        self._data = data
        self._duration = 0 # TODO: calculate duration
        self._samples = 0 # TODO: calculate samples
        self._features = 0
        self._trials = {}
        self._identifier = identifier
        self._start = start
        self._stop = stop

        if self._identifier is None:
            self._identifier = 'recording' + str(len(self._session.Recordings))

        if (data is None) and (location is None):
            raise ValueError('Neither location nor data set in Recording')
        
        if (data is not None) and ((start is None) or (stop is None)):
            raise ValueError('Data specified but stop and/or start were not')

        if data is None:
            # TODO: read from file
            print 'Todo, read data from file'
        else:
            self._samples = self._data.shape[0]
            self._duration = self._samples / self._session.Setup.Frequency
        
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

    @property
    def Data(self):
        if (self.Start is not None) and (self.Stop is not None):
            return self.Data.iloc[self.Start : self.Stop]
        return self._data

    @property
    def Duration(self):
        return self._duration

    @property
    def Samples(self):
        return self.Samples
    
    @property
    def Start(self):
        return self._start

    @property
    def Stop(self):
        return self._stop

    @Data.setter
    def Data(self, data):
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Features):
            self.Data[self.Start : self.Stop] = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in recording ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
                'shape' + str(data.shape)
            ))

    @Session.setter
    def Session(self, session):
        self._session = session

    @Location.setter
    def Location(self, location):
        self._location = location

    @Trials.setter
    def Trials(self, trials):
        self._trials = trials

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
        else:
            raise IndexError('Trial with name ' + name + ' already member of recording')

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
                the recording.
            stop (float): Stop point of trial in seconds relative to the stop point of
                the recording.
            identifier (string): Identifier of the trial. For example *bizeps_curl*

        Attributes:
            recording (Recording): The recording this trial belongs to. Necessary to
                retrieve informations about the setting.
            start (float): Start point of trial in miliseconds relative to the start point
                of the recording.
            startIdx (int): Offset relative to beginning of recording of trial. Index
                to DataFrame
            stopIdx (int): End of trial relative to recording. Index to DataFrame
            stop (float): Stop point of trial in miliseconds relative to the stop point of
                the recording.
            identifier (string): Identifier of the trial. For example *bizeps_curl*
    """

    def __init__(self, recording, start, stop, identifier):
        self._recording = recording
        self._start = start
        self._stop = stop
        self._startIdx = 0
        self._stopIdx = 0
        self._identifier = identifier
        self._samples = 0
        
        if self._name is None:
            self._name = 'trial' + str(len(self._recording.Trials))
        
        if self._start > self._stop:
            raise ValueError((
                'Start point of trial ' + self._identifier + ' bigger than ' +
                'stoppoing point'
            ))

        # Convert frequency to samples/milisecondsy
        f = recording.Setting.Setup.Frequency / 1000
        self._startIdx = self._start * f
        self._stopIdx = self._stop * f
        self._samples = self._stopIdx - self._startIdx
        
        self._recording.putTrial(self)

    @property
    def Name(identifier):
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
    def Stop(self):
        return self._stop

    @property
    def StopIdx(self):
        return self._stopIdx 
    
    @property
    def Samples(self):
        return self._samples

    @Identifier.setter
    def name(self, identifier):
        self._identifier = identifier
    @Recording.setter
    def Recording(self, recording):
        self._recording = recording

    @Start.setter
    def Start(self, start):
        self._start = start

    @Stop.setter
    def Stop(self, stop):
        self._stop = stop

    def getData(self):
        offset = self.Recording.Start
        return self.Recording.Data.iloc[self.StartIdx + offset : self.StopIdx + offset]

    def setData(self, data):
        if (data.shape[0] == self.Samples) and (data.shape[1] == self.Recording.Features):
            self.Recording.Data[self.StartIdx + offset : self.StopIdx + offset] = data
        else:
            raise ValueError((
                'Shape missmatch replacing data in trial ' + self.Identifier + '. ' +
                '\nExpected shape(' + self.Samples + ',' + self.Features + ', got ' +
                'shape' + str(data.shape)
            ))
