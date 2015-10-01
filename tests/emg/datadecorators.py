import numpy as np
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import logging
from nose.tools import with_setup
import emg.datadecorators as datadecorators
import model.model as model
logging.basicConfig(level=logging.DEBUG)

class AbstractDataDecoratorTest(object):
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
        cls.logger = logging.getLogger('DataDecoratorTestLogger')
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


class SamplingDecoratorTest(AbstractDataDecoratorTest):
    def test_downsample(self):
        container = model.DataContainer.from_array(
                np.arange(100).reshape(50, 2),
                10
                )
        decorator = datadecorators.SamplingDecorator(5, None, False)
        ret = decorator._downsample(container.frequency, container)
        assert ret.shape[1] == 2, 'Second dimension errorenous'
        assert ret.shape[0] == 25, 'First dimension errorenous, expected ' + \
                '{} got {}'.format(25, ret.shape[0])
        self.logger.debug(ret)

    def test_upsample(self):
        container = model.DataContainer.from_array(
                np.arange(10).reshape(5, 2),
                10
                )
        decorator = datadecorators.SamplingDecorator(20, None, False)
        ret = decorator._upsample(container.frequency, container)
        assert ret.shape[1] == 2, 'Second dimension errorenous'
        assert ret.shape[0] == 10, 'First dimension errorenous, expected ' + \
                '{} got {}'.format(10, ret.shape[0])
        self.logger.debug(ret)

    def test_iterator_down(self):
        decorator_down = datadecorators.SamplingDecorator(
                frequency=5,
                data_holding_element=self.experiment,
                as_iterator=True
                )
        counter = 0
        for trial in decorator_down.get_data(**{'modality': 'emg'}):
            assert trial.data.shape[0] == 10, 'Wrong number of samples, ' + \
                    'expected 10 got {} by sr of {}'.format(trial.data.shape[0],
                            trial.frequency)
                    # Ten: 200 elements, sr of 20, trial length 2s -> 40 samples
                    # downsampling factor 4 --> 10
            counter += 1
        assert counter == 10, 'wrong number of interations returned: {}'.format(counter)

    def test_iterator_up(self):
        decorator_down = datadecorators.SamplingDecorator(
                frequency=40,
                data_holding_element=self.experiment,
                as_iterator=True
                )
        counter = 0
        for trial in decorator_down.get_data(**{'modality': 'emg'}):
            assert trial.data.shape[0] == 80, 'Wrong number of samples, ' + \
                    'expected 80 got {} by sr of {}'.format(trial.data.shape[0],
                            trial.frequency)
                    # Ten: 200 elements, sr of 20, trial length 2s -> 40 samples
                    # downsampling factor 4 --> 10
            counter += 1
        assert counter == 10, 'wrong number of interations returned: {}'.format(counter)

    def test_return_down(self):
        decorator_down = datadecorators.SamplingDecorator(
                frequency=5,
                data_holding_element=self.experiment,
                as_iterator=False
                )
        trials = decorator_down.get_data(**{'modality': 'emg'})
        assert len(trials) == 10, 'wrong number of interations returned: {}'.format(counter)
        for trial in trials:
            assert trial.data.shape[0] == 10, 'Wrong number of samples, ' + \
                    'expected 10 got {} by sr of {}'.format(trial.data.shape[0],
                            trial.frequency)
                    # Ten: 200 elements, sr of 20, trial length 2s -> 40 samples
                    # downsampling factor 4 --> 10

    def test_return_up(self):
        decorator_down = datadecorators.SamplingDecorator(
                frequency=40,
                data_holding_element=self.experiment,
                as_iterator=False
                )
        trials = decorator_down.get_data(**{'modality': 'emg'})
        assert len(trials) == 10, 'wrong number of interations returned: {}'.format(counter)
        for trial in trials:
            assert trial.data.shape[0] == 80, 'Wrong number of samples, ' + \
                    'expected 80 got {} by sr of {}'.format(trial.data.shape[0],
                            trial.frequency)
                    # Ten: 200 elements, sr of 20, trial length 2s -> 40 samples
                    # downsampling factor 4 --> 10


class WindowDecoratorTest(AbstractDataDecoratorTest):
    def test_iterate(self):
        decorator = datadecorators.WindowDecorator(
                windowsize=0.5,
                stride=0.5,
                data_holding_element=self.experiment,
                as_iterator=True
                )
        counter = 0
        for window in decorator.get_data(**{'modality':'emg'}):
            assert window.shape[0] == 10, 'Expected 10 samples ' + \
                    'got {}'.format(window.shape[0])
            counter += 1
        assert counter == 40, 'Wrong number of windows, expected 40 ' + \
                'but got {}'.format(counter)

    def test_return(self):
        decorator = datadecorators.WindowDecorator(
                windowsize=0.5,
                stride=0.5,
                data_holding_element=self.experiment,
                as_iterator=False
                )
        windows = decorator.get_data(**{'modality':'emg'})
        assert len(windows) == 40, 'Wrong number of windows, expected 40 ' + \
                'but got {}'.format(len(windows))
        for window in windows:
            assert window.shape[0] == 10, 'Expected 10 samples ' + \
                    'got {}'.format(window.shape[0])


class RmsDecoratorTest(AbstractDataDecoratorTest):
    def test_rms(self):
        decorator = datadecorators.RmsDecorator(0.5, None, False)
        container = model.DataContainer.from_array(np.arange(120).reshape(20,6), 10)
        filtered = decorator._rms(5, container)
        assert filtered.shape[0] == container.shape[0] - 4, 'Wrong number of ' + \
                'time steps. Expected {} got {}'.format(container.shape[0] - 4,
                        filtered.shape[0])
        assert filtered.shape[1] == container.shape[1], 'Wrong number of ' + \
                'channels. got {} expected {}'.format(container.shape[1],
                        filtered.shape[1])
        first_element = np.sqrt(np.mean(np.square(np.array([0,6,12,18,24]))))
        assert filtered[0,0] == first_element, 'Error in calculation, ' + \
                'expected {} but was {}'.format(first_element, filtered[0,0])

    def test_iterate(self):
        decorator = datadecorators.RmsDecorator(0.5, self.experiment, True)
        counter = 0
        for trial in decorator.get_data(**{'modality':'emg'}):
            assert trial.shape[0] != 36, 'Wrong number of samples, expected ' + \
                    '36 but got {}'.format(trial.shape[0])
            counter += 1
        assert counter == 10, 'Wrong number of trials, expected 10 ' + \
                'got {}'.format(counter)

    def test_return(self):
        decorator = datadecorators.RmsDecorator(0.5, self.experiment, False)
        trials = decorator.get_data(**{'modality':'emg'})
        assert 10 == len(trials), 'Wrong number of trials, expected 10 ' + \
                'got {}'.format(len(trials))
        for trial in trials:
            assert trial.shape[0] != 36, 'Wrong number of samples, expected ' + \
                    '36 but got {}'.format(trial.shape[0])


class ArrayDecoratorTest(AbstractDataDecoratorTest):
    def test_return(self):
        decorator = datadecorators.ArrayDecorator(self.experiment)
        array = decorator.get_data(**{'modality':'emg'})
        assert array.shape[0] == 10, 'First axis wrong, 10 != {}'.format(array.shape[0])
        assert array.shape[1] == 40, 'Second axis wrong, 40 != {}'.format(array.shape[0])
        assert array.shape[2] == 4, 'THird axis wrong, 4 != {}'.format(array.shape[0])


class PadzeroDecoratorTest(AbstractDataDecoratorTest):
    def test_return(self):
        class Dummy(object):
            def __init__(self):
                self.data = []
                for i in range(2, 12):
                    self.data.append(
                            model.DataContainer.from_array(
                                np.arange(i * 5).reshape(-1, 5),
                                5
                                )
                            )

            def get_data(self, modality=None):
                return self.data


        dummy = Dummy()
        decorator = datadecorators.PadzeroDecorator(dummy, True)
        trials = decorator.get_data(**{'modality':'emg'})
        assert len(trials) == 10, 'Wrong number of trials returned: {}'.format(len(trials))
        for trial in trials:
            assert trial.shape[0] == 11, 'Wrong first dim 11 != {}'.format(trial.shape[0])
            self.logger.debug(trial.data)

