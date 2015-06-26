import cPickle
import math
import numpy as np
import pandas as pd
import scipy.io
import warnings

def jjmdata_from_file(fn):
    with open(fn) as fp:
        # deserialize data
        unpickled = cPickle.load(fp)
    # deserialization returns a tuple containing two lists. Each list contains
    # one ndarray.
    # ndarray at unpickled[0][0]: 12 221 x 160 = 1 955 360 elements
    # reshape the first list s.t. it has 16 columns 122 210 x 16
    emg = unpickled[0][0].reshape((-1, 16))

    # Pos is a 12 221 x 7 array, do these values describe positions
    # in an euclidean space?
    pos = unpickled[1][0]

    return emg, pos


def train_valid_test(devl_emg, devl_pos, test_emg, test_pos,
                     loc=True, rot=True,
                     val_fraction=.2, train_val_gap=1000,
                     window_size=1,
                     emg_frequency=1000,
                     pos_frequency=100):
    # Validate arguments.
    # Further down we reshape emg data. Here we check if it is possible given
    # the elements/dimensions.
    # Fit is calculated using frequencies of pos and emg
    freq_ratio, rest = divmod(emg_frequency, pos_frequency)
    if rest:
        raise ValueError('Frequency if emg is not a multiple of pos frequency')
    if devl_pos.shape[0] * freq_ratio != devl_emg.shape[0]:
        raise ValueError('Length of devl_emg and devl_pos array are not '
                         'related via given frequencies.')
    if test_pos.shape[0] * freq_ratio != test_emg.shape[0]:
        raise ValueError('Length of test_emg and test_pos array are not '
                         'related via given frequencies.')
    if window_size != 1:
        raise ValueError('Window sizes different to 1 not supported')
    if not any([rot, loc]):
        raise ValueError('At least one of rot and loc has to be set to True.')

    # Reshape emg to align with position.
    # Get the number of rows of pos array and reshape the devl_emg and test_emg
    # array s.t. they have the same number of rows and a respective number of
    # columns
    devl_emg = devl_emg.reshape((devl_pos.shape[0], -1))
    test_emg = test_emg.reshape((test_pos.shape[0], -1))

    # Determine indices for validation set.
    n_val_samples = int(math.floor(devl_emg.shape[0] * .2)) - train_val_gap / 2
    n_train_samples = devl_emg.shape[0] - n_val_samples - train_val_gap / 2
    train_emg = devl_emg[:n_train_samples]
    val_emg = devl_emg[-n_val_samples:]
    train_pos = devl_pos[:n_train_samples]
    val_pos = devl_pos[-n_val_samples:]

    # Determine the indices for the targets.
    target_indices = []
    if loc:
        target_indices += [0, 1, 2]
    if rot:
        target_indices += [3, 4, 5, 6]

    return (train_emg, train_pos[:, target_indices],
            val_emg, val_pos[:, target_indices],
            test_emg, test_pos[:, target_indices])

def to_int_labels(labels, arr):
    """ Takes a list of labels as strings and returns a list of integer labels and
        mapping.

        Args:
            labels (List): List of string labels
            arr (np.ndarray): Array with alphanumeric labels
        
        Returns:
            iLbls (numpy.ndarray)
            mapping (Dictionary)
    """
    mapping = {}
    iLbls = np.empty(arr.shape)
    index = 0

    for lbl in labels:
        iLbls[arr == lbl] = index
        mapping[index] = lbl
        index = index + 1

    return iLbls, mapping

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

    header = []
    for h in mat['hs'][0][0][5][0][0][0][0]:
        header.append(h[0])
    ret['kin_data'] = pd.DataFrame(mat['hs'][0][0][5][0][0][1])
    ret['kin_data'].columns = header
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

