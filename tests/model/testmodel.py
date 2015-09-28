import numpy as np
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import model.model as model
import logging
from nose.tools import with_setup

logging.basicConfig(level=logging.DEBUG)


class TestDataContainer(object):
    def __init__(self):
        self.logger = logging.getLogger('TestDataContainer')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        self.logger.addHandler(ch)

    def setup(self):
        self.test_data = np.column_stack((
                np.arange(100),
                np.arange(100, 200),
                np.arange(200, 300)
                ))
        self.frequency = 10
        self.channels = ['flexor', 'brachoradialis', 'novelis']
        self.container = model.DataContainer.from_array(
                self.test_data,
                self.frequency,
                self.channels
                )

    def test_num_channels(self):
        self.logger.debug('type of container: {}'.format(type(self.container)))
        assert self.container.num_channels == 3

    def test_columns(self):
        for i in range(len(self.channels)):
            assert self.channels[i] == self.container.columns[i]

    def test_data(self):
        data = self.container.data
        assert type(data) == np.ndarray
        assert data.shape[0] == self.test_data.shape[0]
        assert data.shape[1] == self.test_data.shape[1]

    def test_dataframe(self):
        frame = self.container.dataframe
        fcolumns = frame.columns
        assert type(frame) == pd.DataFrame
        for i in range(len(self.channels)):
            assert fcolumns[i] == self.channels[i]
        assert frame.shape[0] == self.test_data.shape[0]

    def test_duration(self):
        assert self.container.duration == 10

    def test_getitem(self):
        slice = self.container[2.5:5.5]
        assert type(slice) == model.DataContainer
        assert slice.samples == 30, 'Samples returned are {}'.format(slice.data.shape)
        slice = self.container[5]
        assert type(slice) == model.DataContainer
        assert slice.data.ndim == 2
        assert slice.data.shape[0] == 1

    def test_getitem_border(self):
        slice = self.container[10]
        slice = self.container[0:10]
        assert slice.data.shape[0] == 100

    def test_getitem_fails(self):
        success = True
        try:
            self.container[-4]
            success = False
        except AssertionError as e:
            self.logger.debug(e.message)
            self.logger.info('AssertionEerror for negative value occured')

        try:
            self.container[14:15]
            success = False
        except AssertionError as e:
            self.logger.debug(e.message)
            self.logger.info('AssertionError for start of slice out of bounds' + \
                    'occured')

        try:
            self.container[2:34]
            success = False
        except AssertionError as e:
            self.logger.debug(e.message)
            self.logger.info('AssertionError for stop of slice out of bounds' + \
                    'occured')

    def test_set_data(self):
        new_data = np.arange(60).reshape(20,3)
        self.container.data = new_data
        assert self.container.data.shape[0] == 20
        assert self.container.duration == 2
        assert self.container.samples == 20


class ModelTest(object):
    @classmethod
    def setup(cls):
        """ Creates an Experiment with totaly artificial data. Experiment
            has one setup with two modalities, EMG and kin. EMG has four channels,
            KIN has three channels. Two sessions are "recorded" for two
            different subjects.
            All EMG recordings have sampling rate of 20Hz, all KIN recordings
            sampling rate of 5Hz.
            EMG recording of session1 consists of the following values:
                0       0       0       0.5
                0.1     1       0.01    0.6
                ...     ...     ...     ...
                0.9     9       0.09    1.4
                1.0     10      0.1     1.5
                0.9     9       0.09    1.4
                ...     ...     ...     ...
                0.1     1       0.01    0.6
            Each column is repeated 10 times resulting in a recording of
            20 * 10 = 200 <--> 10s.
            EMG recording of session2 is created from this data by adding
            gaussian noise.
            KIN data for session1 is created from above array by taking the mean
            of all consecutive 4 samples. First channel is the sum of all four
            EMG channels, second channel is the product of all four EMG channels
            along the columns and third channel is square of the first KIN
            channel.
            KIN data for session2 is based on noisy version of above array.
            First channel is the sin of the sum of the four EMG channels along
            the columns, second channel the cosine and third channel the tan.
            As before mean over four samples was taken.
            For each recording five Trials of duration 2s are defined.
        """
        cls.logger = logging.getLogger('ModelTestLogger')
        cls.logger.setLevel(logging.DEBUG)

        s1 = model.Subject('subject1')
        s2 = model.Subject('subject2')

        cls.experiment = model.Experiment()
        cls.experiment.put_subject(s1)
        cls.experiment.put_subject(s2)

        setup1 = model.Setup(cls.experiment)
        modality1 = model.Modality(setup1, 20, 'emg')
        modality2 = model.Modality(setup1, 5, 'kin')

        model.Channel(modality1, 'brachoradialis')
        model.Channel(modality1, 'musculus sterno clavicularis')
        model.Channel(modality1, 'musculus rhombideus')
        model.Channel(modality1, 'musculus lattisimus')

        model.Channel(modality2, 'Pos-X')
        model.Channel(modality2, 'Pos-Y')
        model.Channel(modality2, 'Pos-Z')

        session1 = model.Session(cls.experiment, setup1, s1, 'session1')
        arr = np.column_stack((
                np.tile(
                    np.concatenate((
                        np.arange(0., 1., 0.1),
                        np.arange(1., 0., -0.1)
                        )),
                    10
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(10),
                        np.arange(10, 0, -1)
                        )),
                    10
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(0.0, 0.1, 0.01),
                        np.arange(0.1, 0.0, -0.01)
                        )),
                    10
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(0.5, 1.5, 0.1),
                        np.arange(1.5, 0.5, -0.1)
                        )),
                    10
                    ),
                ))
        recording1 = model.Recording(session1, modality1, data=arr,
                identifier='emg_recording1')

        arr2 = np.column_stack((
                np.sum(np.mean(arr.reshape(-1, 4, 4), axis=1), axis=1),
                np.prod(np.mean(arr.reshape(-1, 4, 4), axis=1), axis=1),
                np.square(np.sum(np.mean(arr.reshape(-1, 4, 4), axis=1), axis=1))
                ))
        recording2 = model.Recording(session1, modality2, data=arr2,
                identifier='kin_recording1')
        for i in range(5):
            model.Trial(recording1, i * 2, 2)
            model.Trial(recording2, i * 2, 2)

        session2 = model.Session(cls.experiment, setup1, s2, 'session2')
        arr = np.add(arr, np.random.randn(*arr.shape))
        recording1 = model.Recording(session2, modality1, data=arr,
                identifier='emg_recording2')
        arr2 = np.column_stack((
            np.sin(np.mean(np.sum(arr.reshape(-1, 4, 4), axis=1))),
            np.cos(np.mean(np.sum(arr.reshape(-1, 4, 4), axis=1))),
            np.tan(np.mean(np.sum(arr.reshape(-1, 4, 4), axis=1)))
            ))
        recording2 = model.Recording(session2, modality2, data=arr2,
                identifier='kin_recording2')
        for i in range(5):
            model.Trial(recording1, i * 2, 2)
            model.Trial(recording2, i * 2, 2)

    def test_model_definition(self):
        self.logger.debug(self.experiment.recursive_to_string())


class ExperimentTest(ModelTest):
    def test_get_recording(self):
        recording = self.experiment.get_recording('emg_recording', 'session1')
        assert recording.identifier == 'emg_recording'

    def test_get_trial(self):
        trials = ['trial0', 'trial1', 'trial2', 'trial3', 'trial4']
        for trial in trials:
            t = self.experiment.get_trial(trial, 'session1', 'emg_recording1')
            assert t.identifier == trial


class TrialTest(ModelTest):
    def test_start(self):
        trials = ['trial0', 'trial1', 'trial2', 'trial3', 'trial4']
        start = 0
        for tid in trials:
            trial = self.experiment.get_trial(
                    session='session1',
                    recording='emg_recording1',
                    identifier=tid
                    )
            assert trial.start == start, 'Start does not match. Start should' + \
                    'be {} but is {}'.format(start, trial.start)
            start += 2

    def test_duration(self):
        trials = ['trial0', 'trial1', 'trial2', 'trial3', 'trial4']
        duration = 2
        for tid in trials:
            trial = self.experiment.get_trial(
                    session='session1',
                    recording='emg_recording1',
                    identifier=tid
                    )
            assert trial.duration == duration, 'Start does not match. Start should' + \
                    'be {} but is {}'.format(duration, trial.duration)

    def test_samples(self):
        trials = ['trial0', 'trial1', 'trial2', 'trial3', 'trial4']
        for tid in trials:
            trial = self.experiment.get_trial(
                    session='session1',
                    recording='emg_recording1',
                    identifier=tid
                    )
            assert trial.samples == 40, 'Start does not match. Start should' + \
                    'be {} but is {} for emg rec'.format(40, trial.samples)

            trial = self.experiment.get_trial(
                    session='session1',
                    recording='kin_recording1',
                    identifier=tid
                    )
            assert trial.samples == 10, 'Start does not match. Start should' + \
                    'be {} but is {} for kin rec'.format(5, trial.samples)

    def test_get_data(self):
        control_emg = np.column_stack((
                np.tile(
                    np.concatenate((
                        np.arange(0., 1., 0.1),
                        np.arange(1., 0., -0.1)
                        )),
                    2
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(10),
                        np.arange(10, 0, -1)
                        )),
                    2
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(0.0, 0.1, 0.01),
                        np.arange(0.1, 0.0, -0.01)
                        )),
                    2
                    ),
                np.tile(
                    np.concatenate((
                        np.arange(0.5, 1.5, 0.1),
                        np.arange(1.5, 0.5, -0.1)
                        )),
                    2
                    ),
                ))
        control_kin = np.column_stack((
                np.sum(np.mean(control_emg.reshape(-1, 4, 4), axis=1), axis=1),
                np.prod(np.mean(control_emg.reshape(-1, 4, 4), axis=1), axis=1),
                np.square(np.sum(np.mean(control_emg.reshape(-1, 4, 4), axis=1), axis=1))
                ))
        trials = ['trial0', 'trial1', 'trial2', 'trial3', 'trial4']
        for tid in trials:
            trial = self.experiment.get_trial(
                    session='session1',
                    recording='emg_recording1',
                    identifier=tid
                    )
            data = trial.get_data()
            assert data.shape == control_emg.shape, ('EMG trial {} ' + \
                    'has not matching shape. Shape of data: {}, shape ' + \
                    'of control: {}').format(tid, data.shape, control_emg.shape)
            assert np.mean(np.equal(data.data, control_emg)) == 1, 'EMG trial {} ' + \
                    'has not matching elements'.format(tid)
            data = trial.get_data(channels=['musculus lattisimus', 'brachoradialis'])
            assert np.mean(np.equal(data.data, control_emg[:,0:2])) == 1, 'slicing' + \
                    'columns errorenous for emg trial {}'.format(tid)
            data = trial.get_data(begin=0.4, end=1.2)
            assert np.mean(np.equal(data.data, control_emg[8:24])) == 1, \
                    'Returned values for time slicing wrong for emg ' + \
                    'trial {}'.format(tid)

            trial = self.experiment.get_trial(
                    session='session1',
                    recording='kin_recording1',
                    identifier=tid
                    )
            data = trial.get_data()
            assert data.shape == control_kin.shape, 'EMG trial {} ' + \
                    'has not matching shape'.format(tid)
            assert np.mean(np.equal(data.data, control_kin)) == 1, 'KIN trial {} ' + \
                    'has not matching elements'.format(tid)
            data = trial.get_data(channels=['Pos-X', 'Pos-Y'])
            assert np.mean(np.equal(data.data, control_kin[:,0:2])) == 1, 'slicing' + \
                    'columns errorenous for kin trial {}'.format(tid)
            data = trial.get_data(begin=0.4, end=1.2)
            assert np.mean(np.equal(data.data, control_kin[2:6])) == 1, \
                    'Returned values for time slicing wrong for emg ' + \
                    'trial {}'.format(tid)

