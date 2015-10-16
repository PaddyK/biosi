""" This module contains routines to load data from the WAY-EEG-GAL dataset.
    More information on the dataset can be found on http://www.nature.com/articles/sdata201447
"""
import scipy.io
import numpy as np
import pandas as pd


def read_session(path):
    """ Reads a session from a `HS_P#_S#.mat` file. This type of file contains all data
        of a single lift series (EMG, EEG, Position data, environmental data, miscellaneous
        data)

        Args:
            path (String): Path to file containing data

        Returns:
            Dictionary:
                subject --> int (Number of participant/subject)
                session --> int (Number of session of participant)
                initials --> string (initials of subject)
                emg_data --> pandas.core.DataFrame
                emg_sr --> int (Sampling Rate of emg data)
                eeg_data --> pandas.core.DataFrame
                eeg_sr --> int (Sampling Rate of eeg data)
                kin_data --> pandas.core.DataFrame (kinematics data, forces, positions)
                kin_sr --> int (Sampling Rate of kinematics data)
                env_data --> pandas.core.DataFrame (used surface and weight)
                env_sr --> int (Sampling Rate of environment)
                misc_data --> pandas.core.DataFrame (Some additional data)
                misc_sr --> int (Sampling Rate of miscellaneous data)
    """

    mat = scipy.io.loadmat(path)
    ret = {}
    ret['initials'] = mat['hs'][0][0][0][0][0]
    ret['subject'] = mat['hs'][0][0][1][0][0]
    ret['session'] = mat['hs'][0][0][2][0][0]

    ret['emg_data'] = pd.DataFrame(mat['hs'][0][0][3][0][0][0])
    header = []
    for h in mat['hs'][0][0][3][0][0][1][0]:
        header.append(h[0])
    ret['emg_data'].columns = header
    ret['emg_sr'] = mat['hs'][0][0][3][0][0][2][0][0]

    header = []
    for h in mat['hs'][0][0][4][0][0][0][0]:
        header.append(h[0])
    ret['eeg_data'] = pd.DataFrame(mat['hs'][0][0][4][0][0][1])
    ret['eeg_data'].columns = header
    ret['eeg_sr'] = mat['hs'][0][0][4][0][0][2][0][0]

    kin_cols = [
            'Px1 - position x sensor 1',
            'Px2 - position x sensor 2',
            'Px3 - position x sensor 3',
            'Px4 - position x sensor 4',
            'Py1 - position y sensor 1',
            'Py2 - position y sensor 2',
            'Py3 - position y sensor 3',
            'Py4 - position y sensor 4',
            'Pz1 - position z sensor 1',
            'Pz2 - position z sensor 2',
            'Pz3 - position z sensor 3',
            'Pz4 - position z sensor 4'
            ]
    header = []
    for h in mat['hs'][0][0][5][0][0][0][0]:
        header.append(h[0])
    ret['kin_data'] = pd.DataFrame(mat['hs'][0][0][5][0][0][1])
    ret['kin_data'].columns = header
    ret['kin_data'] = ret['kin_data'].loc[:, kin_cols]
    ret['kin_sr'] = mat['hs'][0][0][5][0][0][2][0][0]

    header = []
    for h in mat['hs'][0][0][6][0][0][0][0]:
        header.append(h[0])
    ret['env_data'] = pd.DataFrame(mat['hs'][0][0][6][0][0][1])
    ret['env_data'].columns = header
    ret['env_sr'] = mat['hs'][0][0][6][0][0][2][0][0]

    header = []
    for h in mat['hs'][0][0][7][0][0][0][0]:
        header.append(h[0])
    ret['misc_data'] = pd.DataFrame(mat['hs'][0][0][7][0][0][1])
    ret['misc_data'].columns = header
    ret['misc_sr'] = mat['hs'][0][0][7][0][0][2][0][0]

    return ret

def read_meta_file(path):
    """ Reads a meta file `P3_AllLifts.mat`, parses it and returns content as DataFrame

        Args:
            path (string): Path to meta file

        Returns:
            meta (pandas.core.DataFrame)
    """
    mat = scipy.io.loadmat(path)
    data = mat['P'][0,0]
    headers = []
    for header in data[1][:, 0]:
        headers.append(header[0])
    df = pd.DataFrame(data[0])
    df.columns = headers

    return df

def get_trial_times(meta, session, rec_dur):
    meta_session = meta.loc[meta.loc[:, 'Run'] == session, :]
    meta_session.reset_index(inplace=True)
    start_times = meta_session.loc[:, 'StartTime']
    data = start_times.values
    copy = data.copy()
    data[:-1] = data[1:]
    data[-1] = rec_dur
    times = pd.DataFrame(np.column_stack((copy, data)))
    times.columns = ['start', 'stop']
    return times

def get_event_times(session, meta, event, start, dur=None):
    times = ['Lift', start]
    if dur is not None:
        times.append(dur)
    m = meta.loc[meta.loc[:, 'Run'] == session, :]
    m.reset_index(inplace=True)
    ret = m.loc[:, times]
    ret = pd.concat([
        ret,
        pd.DataFrame([event for i in range(ret.shape[0])], columns=['Event'])
        ], axis=1)
    for i in range(ret.shape[0]):
        ret['Lift'][i] = 'trial{}'.format(i)
#    ret.loc[:, ['Lift', 'Event', start, dur]]
    ret = ret.reindex_axis(['Lift', 'Event', start, dur], axis=1)
    return ret

