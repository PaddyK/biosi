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

