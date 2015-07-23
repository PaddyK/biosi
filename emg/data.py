import cPickle
import math
import numpy as np
import pandas as pd
import scipy.io
import warnings
import breze.data

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

def align_and_label_recordings(session, target_modality, split=(.5, .25, .25),
        alignment_method='mean', include=None, exclude=None, skip=0):
    """ Returns training, validation and testing set (for each on set containing
        the data and one set containing the labels)

        Args:
            session (model.model.Session): Session from which sets should be
                created
            target_modality (String): Identifier of the modality serving as
                target
            split (Tuple, optional): Size of set in percent
                (size_train, size_test, size_val)
            alignment_method (String, optional): How to align recordings of
                different modalities (i.e. give them the same length)
            include (List, optional): List of recording identifier (Strings). If
                set only specified recordings will be used for data matrix
            exclude (List, optional): List of recording identifier (String). If
                set all recordings but those specified will serve as data
            skip (int): How many samples to skip between test, train and
                validation set

        Note:
            Supported Arguments for ``alignment_method``:
                mean: Aligns recordings by taking the mean of a subset of samples
                    of longer recording (``recording1`` with 4000Hz, ``recording2`` with
                    500Hz --> align by taking mean over 4 samples of ``recording1``)
                median: Same as mean.
                slice: Align recordings by folding samples into second dimension.
                    With the example from ``mean`` and assuming recording has
                    4 columns. When using split ``recording1`` will have the same
                    length as recording2 but 16 instead of 4 columns.
                    This method kind of destroys the timely dimension.

        Raises:
            ValueError if unknown keyword for *alignment_method* encountered
    """
    p_train, p_val, p_test = split
    assert (p_train + p_val + p_test) == 1, 'Sum of percentual values for ' + \
            'training, validation and test set greater than one. Values ' + \
            'were {}, {}, {}'.format(p_train, p_val, p_test)

    # Retrieve all specified recordings and the target recording
    data_recordings = []
    target_recording = None
    for recording in session.Recordings.itervalues():
        if recording.Modality == target_modality:
            target_recording = recording
        elif include is not None:
            if recording.Identifier in include:
                data_recordings.append(recording)
        elif exclude is not None:
            if recording.Identifier not in exclude:
                data_recordings.append(recording)
        else:
            data_recordings.append(recording)

    if len(data_recordings) == 0:
        raise ValueError('Could not find any of the trials included ' + \
                'in "include". Error occured in emg.data.' + \
                'train_valid_test_from_modalities'
                )

    if target_recording is None:
        raise ValueError('Could not find target modality. Modality was {}. ' + \
                'Error occured in emg.data.train_valid_test_from_modalities'
                .format(target_modality)
                )

    # Reduce length of all arrays to the length of the target array
    target_done = False
    aligned = {}
    for recording in data_recordings:
        if alignment_method == 'mean':
            aligned[recording.Identifier] = align_by_mean(
                    recording,
                    target_recording
                    )
        elif alignment_method == 'median':
            aligned[recording.Identifier] = align_by_median(
                    recording,
                    target_recording
                    )
        elif alignment_method == 'collapse':
            aligned[recording.Identifier] = align_by_collapse(
                    recording,
                    target_recording
                    )
        else:
            raise ValueError('Unknown value for keyword "alignment_method" ' + \
                    'encountered. Value was: {}'.format(alignment_method)
                    )
    train_X = None
    val_X = None
    test_X = None
    train_Y = None
    val_Y = None
    test_Y = None
    target_trials = target_recording.get_trials_as_list()
    target_done = False

    # Create test, training and validation set
    for rec in data_recordings:
        start = 0
        end = target_recording.shape[0] * p_train
        train_tmp = rec[start:int(end-skip/2), :]
        if not target_done:
            train_Y = target_recording[start:int(end-skip/2), :]

        start = end
        end = end + target_recording.shape[0] * p_val
        val_tmp = rec[int(start + skip/2):int(end - skip/2), :]
        if not target_done:
            val_Y = target_recording[int(start + skip/2):int(end - skip/2), :]

        start = end
        test_tmp = rec[int(start + skip/2):rec.shape[0], :]
        if not target_done:
            test_Y = target_recording[int(start + skip/2):rec.shape[0], :]
            target_done = True

        if train_X is None:
            train_X = train_tmp
            val_X = val_tmp
            test_X = test_tmp
        else:
            train_X = np.column_stack(train_X, train_tmp)
            val_X = np.column_stack(val_X, val_tmp)
            test_X = np.column_stack(test_X, test_tmp)

    return (train_X, train_Y, val_X, val_Y, test_X, test_Y)

def get_min_length(data_sets):
    """ Returns the size of the smalles data set along the first axis

        Args:
            data_set (List): List of np.ndarrays or anything with ``.shape``
                property

        Returns:
            min_length (int)
    """
    min_length = -1
    for e in data_sets:
        if min_length == -1:
            min_length = e.shape[0]
        elif e.shape[0] < min_length:
            min_length = e.shape[0]
    return min_length

def align_by_mean(to_align, align_on):
    """ Aligns trials of two recordings by taking the mean.

        Example:
            If recording ``to_align`` was recorded using 4000Hz and ``align_on``
            recorded with 500Hz, when the mean over 8 samples of ``to_align``
            is taken

        Args:
            to_align (model.model.Recording): Recording on which mean should
                be applied (needs to have larger sampling rate)
            align_on (model.model.Recording): Recording to align on

        Returns:
            List of np.ndarrays

        Raises:
            AssertionError if ``to_align`` has smaller sampling rate/frequency
            than ``align_on''
    """
    assert to_align.get_frequency() > align_on.get_frequency(), 'Frequency ' + \
            'of recording for which first dimension of trials should be ' + \
            'reduced has higher frequency than recording it should be ' + \
            'aligned to. {}: {}Hz, {}: {}Hz'.format(
                    to_align.Identifier, to_align.get_frequency(),
                    align_on.Identifier, align_on.get_frequency()
                    )
    ret = []
    arr, n = _get_settings_for_alignment(to_align, align_on)
    trials = arr.get_trials_as_list(pandas=False)
    for trial in trials:
        steps, remainder = divmod(trial.shape[0], n)
        tmp = np.mean(trial[0:n, :], axis=0)

        for step in range(1, steps):
            start = step * n
            stop = (step + 1) * n
            tmp = np.row_stack([tmp, np.mean(trial[start:stop, :], axis=0)])
        ret.append(tmp)
    return ret

def align_by_median(to_align, align_on):
    """ Aligns trials of two recordings by taking the median.

        Example:
            If recording ``to_align`` was recorded using 4000Hz and ``align_on``
            recorded with 500Hz, when the median over 8 samples of ``to_align``
            is taken

        Args:
            to_align (model.model.Recording): Recording on which median should
                be applied (needs to have larger sampling rate)
            align_on (model.model.Recording): Recording to align on

        Returns:
            List of np.ndarrays

        Raises:
            AssertionError if ``to_align`` has smaller sampling rate/frequency
            than ``align_on''
    """
    assert to_align.get_frequency() > align_on.get_frequency(), 'Frequency ' + \
            'of recording for which first dimension of trials should be ' + \
            'reduced has higher frequency than recording it should be ' + \
            'aligned to. {}: {}Hz, {}: {}Hz'.format(
                    to_align.Identifier, to_align.get_frequency(),
                    align_on.Identifier, align_on.get_frequency()
                    )
    ret = []
    arr, n = _get_settings_for_alignment(to_align, align_on)
    trials = arr.get_trials_as_list(pandas=False)
    for trial in trials:
        steps, remainder = divmod(trial.shape[0], n)
        tmp = np.median(trial[0:n, :], axis=0)

        for step in range(1, steps):
            start = step * n
            stop = (step + 1) * n
            tmp = np.row_stack([tmp, np.median(trial[start:stop, :], axis=0)])
        ret.append(tmp)
    return ret

def align_by_collapse(to_align, align_on):
    """ Given two recordings aligns all trials to have the same first
        dimension by collapsing rows of the trial recorded with higher
        frequencies into second dimension.

        If size of first dimension in a trial is not a multiple of
        ``columns * factor`` trial is cut of. ``factor`` is the ration
        between frequencies.

        Example:
            Trial has shape ``(20, 2)``, ``factor=3`` then
            20 * 2 / (2 * 3) = 40 / 6 = 6 rest 4 --> 4 samples are ommitted

        Args:
            to_align (model.model.Recording): First recording to align
            align_on (model.model.Recording): Second recording to align

        Returns:
            List of numpy.ndarray
    """
    assert to_align.get_frequency() > align_on.get_frequency(), 'Frequency ' + \
            'of recording for which first dimension of trials should be ' + \
            'reduced has higher frequency than recording it should be ' + \
            'aligned to. {}: {}Hz, {}: {}Hz'.format(
                    to_align.Identifier, to_align.get_frequency(),
                    align_on.Identifier, align_on.get_frequency()
                    )

    to_collapse, n = _get_settings_for_alignment(to_align, align_on)
    trials = to_collapse.get_trials_as_list(pandas=False)
    ret = breze.data.collapse(trials, n)
    return ret

def _get_settings_for_alignment(recording_one, recording_two):
    """ Given two trials gets the one with higher frequency and ration of
        frequencies.

        Args:
            recording_one (model.model.Recording): First trial
            recording_two (model.model.Recording): Second trial

        Returns:
            to_collapse (model.model.Recording): Recording with higher frequency
            n (int) ration between frequences (bigger than one)
    """
    f1 = recording_one.get_frequency()
    f2 = recording_two.get_frequency()
    n = 0
    to_collapse = None

    if f1 < f2:
        n = f2 / f1
        to_collapse = recording_two
    else:
        n = f1 / f2
        to_collapse = recording_one

    return to_collapse, n

def train_valid_test_from_lists(data, target, offset=0, split=(.5, .25, .25)):
        """ Given a list of lists as data and a list as target return
            training, test and validation set.

            Args:
                data (List): List of lists of ndarrays.
                target (List): List of ndarrays - targets to predict
                offset (int, optional): Offset between each set
                split (Tuple, optional): Size of training, validation and test set

            Returns:
                X, Z, XV, ZV, XT, ZT ndarrays with two dimensions where
                the first dimension sample size and the third dimension number
                of features

            Raises:
                AssertionError: Sum of elements of split larger than one or
                    dimensionality missmatch on first dimensionality of
                    concatenated trials
                TypeError: Dimensionality missmatch in first dimension of trials
        """
        ptrain, pval, ptest = split
        assert (ptrain + pval + ptest) == 1, 'Sum of split smaller unequal ' + \
                'to one'

        X_whole = None
        Z_whole = None
        concat_method = None
        if len(target[0].shape) == 1:
            concat_method = np.concatenate
        else:
            concat_method = np.row_stack

        for i in range(len(target)):
            block = data[0][i]
            for j in range(1, len(data)):
                block = np.column_stack([block, data[j][i]])
            if Z_whole is None:
                Z_whole = target[i]
                X_whole = block
            else:
                Z_whole = concat_method([Z_whole, target[i]])
                X_whole = np.row_stack([X_whole, block])

        assert X_whole.shape[0] == Z_whole.shape[0], 'Shape of data and ' + \
                'targets is not the same in data.train_valid_test_from_lists. ' + \
                'data: {}, targets: {}'.format(
                        X_whole.shape[0],
                        Z_whole.shape[0]
                        )
        n = X_whole.shape[0]
        start = 0
        end = int(n * ptrain - offset / 2)
        X = X_whole[start:end, :]
        Z = Z_whole[start:end, :]

        start = int(n * ptrain + offset / 2)
        end = int(n * (ptrain + pval) - offset / 2)
        XV = X_whole[start:end, :]
        XZ = Z_whole[start:end, :]

        start = int(n * (ptrain + pval) + offset / 2)
        end = X_whole.shape[0]
        XT = X_whole[start:end, :]
        ZT = Z_whole[start:end, :]

        return X, Z, XV, XZ, XT, ZT

def sets_for_sequence_learning(sequences, targets, split=(0.5, 0.25, 0.25)):
    """ Creates training, validation and testing set for sequence classification

        Expects windowfied data, collapses data sequences into one vector and
        assigns the last target of the window as target to the collaosed
        sequence.

        Args:
            sequences (List): List of sequences (numpy.ndarrays)
            targets (List): List of targets (numpy.ndarrays)
            split (Tuple): sizes of training, validation and test set

        Returns:
            X, Z, VX, VZ, TX, TZ two dimensional nd_arrays
    """
    p_train, p_val, p_test = split
    flat_sequences = []
    last_targets = []

    for i in range(len(sequences)):
        flat_sequences.append(sequences[i].flatten())
        last_targets.append(targets[i][targets[i].shape[0] - 1, :])

    stop = int(len(flat_sequences) * p_train)
    X = np.row_stack(flat_sequences[:stop])
    Z = np.row_stack(last_targets[:stop])

    start = stop
    stop = int(len(flat_sequences) * (p_train + p_val))
    XV = np.row_stack(flat_sequences[start:stop])
    ZV = np.row_stack(last_targets[start:stop])

    start = stop
    stop = len(flat_sequences)
    XT = np.row_stack(flat_sequences[start:stop])
    ZT = np.row_stack(last_targets[start:stop])

    return X, Z, XV, ZV, XT, ZT

def windowify_labeled_data_set(sequences, targets, length, offset=0, as_list=True):
    """ Windowifies sequences and targets and returns them as three
        dimensional np.ndarray or list.

        Args:
            sequences (List): List on numpy arrays
            targets (List): List of numpy arrays
            length (int): length of windows
            offset (int, optional): Offset between start of windows
            as_list (Boolean, optional): Whether or not to return windowfied
                sets as list

        Returns:
            w_sequences, w_targets
    """
    w_sequences = breze.data.windowify(sequences, length, offset)
    # breze returns three dimensional array with shape (dimensionality of
    # input sequence + 1 --> 1D array --> 2D array)
    # num windows x window length x features in original sequence
    w_targets = breze.data.windowify(targets, length, offset)

    if len(w_targets.shape) == 2:
        w_targets = w_targets[:, :, np.newaxis]
    if len(w_sequences.shape) == 2:
        w_sequences = w_sequences[:, :, np.newaxis]

    if as_list:
        tmps = []
        tmpt = []

        for i in range(w_sequences.shape[0]):
            tmps.append(w_sequences[i, :, :])
            tmpt.append(w_targets[i, :, :])
    w_sequences = tmps
    w_targets = tmpt

    return w_sequences, w_targets

def windowify_nominal_labeled_data_set(sequences, labels, length, offset=1,
        as_list=True):
    """ Windowifies sequences and broadcasts respective label accordingly.

        It is expected that each sequence has one label in labels. Each
        sequence gets windowified and the respective label is added accordingly
        for each window.

        Args:
            sequences (List): List of numpy.ndarrays
            labels (List): List of strings
            length (int): Number samples each window contains
            offset (int, optional): Distance in sample between beginning of two
                consecutive windows
            as_list (Boolean): Return windowfied sequences and labels as lists
                or arrays

        Note:
            If `as_list=False` three-dimensional array is returned with
            *num trials x windowsize x num features*.
            Labels are also returned as three dimensional array with shape
            *num trials x windowsize x 1*, i.e. each sample has a trial.

            If `as_list=True` windows are returned as list and labels are
            returned as list. As opposed to `as_list=True`, each **window**
            has one label (and *not* each sample!)

        Returns:
            w_sequences, List of Arrays or 3D array
            w_labels, List of strings or 3D array
    """
    windows = []
    for i in range(len(sequences)):
        # Breze will return a three dimensional array, where the first
        # dimension is the number of windows made out of the trials
        #
        # So for each original sequence we have one array of windows. Thus
        # mapping of labels is retained
        windows.append(breze.data.windowify([sequences[i]], length, offset))

    w_sequences = None
    w_labels = None

    if as_list:
        w_sequences = []
        w_labels = []
        for i in range(len(windows)):
            for j in range(windows[i].shape[0]):
                # For each windowified trial go through each window (first
                # dimension) and append it to a list.
                w_sequences.append(windows[i][j])
                w_labels.append(labels[i])
    else:
        # Concatenate windows along the first axis to get one big array
        # Copy label for each sample in each window and also create a
        # three  dimensional array with the same two first dimensions
        w_sequences = windows[0]
        w_labels = np.repeat(
                labels[0],
                windows[0].shape[0] * windows[0].shape[1]
                ).reshape(windows[0].shape[0], windows[0].shape[1])
        for i in range(1, len(windows)):
            w_sequences = np.concatenate((w_sequences, windows[i]), axis=0)
            w_labels = np.concatenate((
                    w_labels,
                    np.repeat(
                        labels[i],
                        windows[i].shape[0] * windows[i].shape[1]
                        ).reshape(
                            windows[i].shape[0],
                            windows[i].shape[1]
                            )
                    ),axis=0
                    )
        w_labels = w_labels[:, :, np.newaxis]
    return w_sequences, w_labels

def padzeros(sequences, as_list=True, front=False):
    """ Returns sequences of unit length by padding shorter sequences with
        zeros.

        Args:
            sequences (List): List of np.ndarrays
            as_list (Boolean): If true return as list of arrays, if false
                return as three dimensional array with
                ``num trials x num samples x num features``
            front (Boolean): If True pad zeros from the front, else from the
                back

        Returns:
            three dimensional array of shape trials x samples x features
            Or list of ndarrays
    """
    padded = breze.data.padzeros(sequences, front=front)
    if as_list:
        # Returns ith trial, if padded is three-D the same as padded[i, :, :]
        tmp = [padded[i] for i in range(padded.shape[0])]
        padded = tmp
    return padded
