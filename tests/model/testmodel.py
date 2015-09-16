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


class AbstractModelTest(object):
    @classmethod
    def setup(cls):
        s1 = model.Subject('subject1')
        s2 = model.Subject('subject2')

        cls.expepriment = model.Experiment()
        cls.expepriment.set_subject(s1)
        cls.expepriment.set_subject(s2)

        setup1 = model.Setup(cls.expepriment)
        modality1 = model.Modality(setup1, 20, 'emg')
        modality2 = model.Modality(setup1, 5, 'kin')

        model.Channel(modality1, 'brachoradialis')
        model.Channel(modality1, 'musculus sterno clavicularis')
        model.Channel(modality1, 'musculus rhombideus')
        model.Channel(modality1, 'musculus lattisimus')

        model.Channel(modality2, 'Pos-X')
        model.Channel(modality2, 'Pos-Y')
        model.Channel(modality2, 'Pos-Z')

        session1 = model.Session(cls.expepriment, setup1, s1, 'session1')
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
                identifier='emg_recording')
        for i in range(5):
            model.Trial(recording1,i * 2, 2)

        arr2 = np.column_stack((
                np.mean(np.sum(arr, axis=1).reshape(-1, 4, 4), axis=1),
                np.mean(np.prod(arr, axis=1).reshape(-1, 4, 4), axis=1),
                np.mean(np.square(arr, axis=1).reshape(-1, 4, 4), axis=1)
                ))
        recording2 = model.Recording(session2, modality1, data=arr2,
                identifier='kin_recording')
        for i in range(5):
            model.Trial(recording2, i * 2, 2)

        session2 = model.Session(cls.expepriment, setup1, s2, 'session2')
        arr = np.add(arr, np.random.randn(*arr.shape))
        recording1 = model.Recording(session2, modality1, data=arr,
                identifier='emg_recording')
        arr2 = np.column_stack((
            np.mean(np.sin(np.sum(arr, axis=1)).reshape(-1, 4, 4)),
            np.mean(np.cos(np.sum(arr, axis=1)).reshape(-1, 4, 4)),
            np.mean(np.tan(np.sum(arr, axis=1)).reshape(-1, 4, 4))
            ))
        for i in range(5):
            model.Trial(recording1, i * 2, 2)
            model.Trial(recording2, i * 2, 2)


