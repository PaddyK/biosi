import model
import numpy as np
import pandas as pd
import warnings
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(os.path.join(__file__, os.path.pardir))),
    'emg'
    ))
import emg.data

def create_kb(data = None):
    if data is None:
        print 'Create new dataset...'
        rec1 = np.arange(100)
        rec1 = np.column_stack((rec1,rec1,rec1))

        rec2 = np.arange(100,200)
        rec2 = np.column_stack((rec2,rec2,rec2))

        rec3 = np.arange(200,300)
        rec3 = np.column_stack((rec3,rec3,rec3))

        data = np.row_stack((rec1,rec2,rec3))
    df = pd.DataFrame(data, dtype = 'float')

    experiment = model.Experiment()

    # Subjects
    #==========
    so1 = model.Subject('Robert')
    so2 = model.Subject('Therese')
    so3 = model.Subject('Michael')
    experiment.put_subject(so1)
    experiment.put_subject(so2)
    experiment.put_subject(so3)

    # Setups
    # =======
    setup = model.Setup(experiment)
    modality = model.Modality(setup, 1, 'arm')
    model.Sample(modality, 'bizeps')
    model.Sample(modality, 'trizeps')

    modality = model.Modality(setup, 'leg')
    model.Sample(modality, 'gluteus maximus')

    # Sessions
    # =========

    # Session1
    #---------
    session = model.Session(experiment, setup, so1)
    recording = model.Recording(session = session, data = df)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')

    # Session 2
    # ----------
    df = pd.DataFrame(np.copy(data), dtype = 'float')
    session = model.Session(experiment, setup, so2)
    recording = model.Recording(session = session, data = df)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')

    df = pd.DataFrame(np.copy(data), dtype = 'float')
    recording = model.Recording(session=session, data=df)
    model.Trial(recording, 10, 10, 'curl_simple2')
    model.Trial(recording, 30, 11, 'squat2')
    model.Trial(recording, 50, 12, 'curl_difficult2')
    model.Trial(recording, 70, 20, 'leg_lever2')


    # Session 3
    # ----------
    df = pd.DataFrame(np.copy(data), dtype = 'float')
    session = model.Session(experiment, setup, so3)
    recording = model.Recording(session = session, data = df)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')

    return experiment

def small_sport_kb():
    experiment = model.Experiment()

    # Subjects
    # -----------------------------------------------------------------------------------
    so3 = model.Subject('subject3')
    experiment.put_subject(so3)

    # Setups
    # ===================================================================================
    setup = model.Setup(experiment)
    modality = model.Modality(
            setup=setup,
            frequency=4000,
            identifier='arm'
            )
    model.Sample(modality, 'bizeps')
    model.Sample(modality, 'triceps')
    model.Sample(modality, 'extensor_digitorum')
    model.Sample(modality, 'flexor_digitorum')

    # Sessions
    # ===================================================================================

    # Session 3
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_01.pkl',
        modality=modality.Identifier
    )
    t = model.Trial(rec, 0, 4, 'calm')
    t.add_marker((4, 'start_trials'))
    t.add_marker((4.1,'another'))
    model.Trial(rec, 4, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 8, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 12, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 16, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 20, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 24, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 28, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 32, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 36, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 44, 4, 'max_triceps').add_marker((0, 'start_max_tests'))
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_bizeps')
    model.Trial(rec, 60, 4, 'max_extensor')

    return experiment

def sport_kb():
    experiment = model.Experiment()

    # Subjects
    # -----------------------------------------------------------------------------------
    so3 = model.Subject('subject1')
    experiment.put_subject(so3)
    so3 = model.Subject('subject2')
    experiment.put_subject(so3)
    so3 = model.Subject('subject3')
    experiment.put_subject(so3)
    so3 = model.Subject('subject4')
    experiment.put_subject(so3)
    so3 = model.Subject('subject5')
    experiment.put_subject(so3)
    so3 = model.Subject('subject6')
    experiment.put_subject(so3)
    so3 = model.Subject('subject7')
    experiment.put_subject(so3)
    so3 = model.Subject('subject8')
    experiment.put_subject(so3)
    so3 = model.Subject('subject9')
    experiment.put_subject(so3)
    so3 = model.Subject('subject10')
    experiment.put_subject(so3)

    # Setups
    # ===================================================================================
    setup = model.Setup(experiment)
    modality = model.Modality(
            setup=setup,
            frequency=4000,
            identifier='arm'
            )
    model.Sample(modality, 'bizeps')
    model.Sample(modality, 'triceps')
    model.Sample(modality, 'extensor_digitorum')
    model.Sample(modality, 'flexor_digitorum')

    # Sessions
    # ===================================================================================

    # Session 1
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_01.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 8, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 12, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 16, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 20, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 24, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 28, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 32, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 36, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 44, 4, 'max_bizeps')
    model.Trial(rec, 48, 4, 'max_triceps')
    model.Trial(rec, 52, 4, 'max_flexor')
    model.Trial(rec, 56, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 2
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_02.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 8, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 12, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 16, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 20, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 24, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 28, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 32, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 36, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 3
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_03.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 8, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 12, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 16, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 20, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 24, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 28, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 32, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 36, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 52, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 56, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 4
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_04.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 8, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 12, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 16, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 20, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 24, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 28, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 32, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 36, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 5
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_05.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 8, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 12, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 16, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 20, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 24, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 28, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 32, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 36, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 44, 4, 'max_bizeps')
    model.Trial(rec, 48, 4, 'max_triceps')
    model.Trial(rec, 52, 4, 'max_flexor')
    model.Trial(rec, 56, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 6
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_06.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 8, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 12, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 16, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 20, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 24, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 28, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 32, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 36, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 7
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_07.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 8, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 12, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 16, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 20, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 24, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 28, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 32, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 36, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 44, 4, 'max_bizeps')
    model.Trial(rec, 48, 4, 'max_triceps')
    model.Trial(rec, 52, 4, 'max_flexor')
    model.Trial(rec, 56, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 8
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_08.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 8, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 12, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 16, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 20, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 24, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 28, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 32, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 36, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 44, 4, 'max_bizeps')
    model.Trial(rec, 48, 4, 'max_triceps')
    model.Trial(rec, 52, 4, 'max_flexor')
    model.Trial(rec, 56, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 9
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_09.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 8, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 12, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 16, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 20, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 24, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 28, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 32, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 36, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_extensor')

    # Sessions
    # ===================================================================================

    # Session 10
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/Proband_10.pkl',
        modality = modality.Identifier
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'hantel1', label = 'hantel')
    model.Trial(rec, 8, 4, 'hantel2', label = 'hantel')
    model.Trial(rec, 12, 4, 'hantel3', label = 'hantel')
    model.Trial(rec, 16, 4, 'reverse_kettle1', label = 'reverse_kettle')
    model.Trial(rec, 20, 4, 'reverse_kettle2', label = 'reverse_kettle')
    model.Trial(rec, 24, 4, 'reverse_kettle3', label = 'reverse_kettle')
    model.Trial(rec, 28, 4, 'stomach_kettle1', label = 'stomach_kettle')
    model.Trial(rec, 32, 4, 'stomach_kettle2', label = 'stomach_kettle')
    model.Trial(rec, 36, 4, 'stomach_kettle3', label = 'stomach_kettle')
    model.Trial(rec, 40, 4, 'max_bizeps')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_extensor')
    return experiment

def create_emg_eeg_kb(meta, sessions, markers=None):
    """ Builds an `emgframework.model.model.Experiment` using information extracted from
        `P#_AllLifts.mat` and data extracted from `HS_P#_S#.mat`.
        Builds the model with EMG and EEG data only (Kinematic, Environmental and
        Miscellaneous data not included)

        Args:
            meta (pandas.core.DataFrame): Meta information to sessions
            session (Dictionary): Data of one session

        Returns:
            emgframework.model.model.Experiment
    """
    cols = [col for col in meta.columns if col.startswith('t') or col.startswith('Dur_')]
    meta.loc[:,cols] = meta.loc[:, cols] - 2.002
    # Define mapping for weights and surface
    weights = {}
    weights[1] = '165g'
    weights[2] = '330g'
    weights[4] = '660g'
    surface = {}
    surface[1] = 'sandpaper'
    surface[2] = 'suede'
    surface[3] = 'silk'

    # Create Experiment
    # ==================================================================================
    exp = model.Experiment()
    subj = model.Subject(sessions[0]['initials'])

    # Creating Setup and Modalities
    # ==================================================================================
    setup = model.Setup(exp)
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
    mod_emg = model.Modality(setup, sessions[0]['emg_sr'], 'emg')
    for s in sessions[0]['emg_data'].columns:
        model.Sample(mod_emg, s)
    mod_eeg = model.Modality(setup, sessions[0]['eeg_sr'], 'eeg')
    for s in sessions[0]['eeg_data'].columns:
        model.Sample(mod_eeg, s)
    mod_kin = model.Modality(setup, sessions[0]['kin_sr'], 'kin')
    for s in sessions[0]['kin_data'].columns:
        if s in kin_cols:
            model.Sample(mod_kin, s)

    # Creating Session, Recordings and Trials
    # ==================================================================================
    for session in sessions:
        # Select data of from metadata belonging to in `session` specified session
        meta_session = meta.loc[meta.loc[:, 'Run'] == session['session'], :]
        meta_session.reset_index(inplace=True)
        sess = model.Session(exp, setup, subj, 'session_' + str(session['session']))
        # Creating Recordings
        # ----------------------------------------------------------------------------------
        rec_emg = model.Recording(
                sess,
                data=session['emg_data'],
                identifier='emg_data',
                modality = mod_emg.Identifier
            )
        rec_eeg = model.Recording(
                sess,
                data=session['eeg_data'],
                identifier='eeg_data',
                modality = mod_eeg.Identifier
            )
        rec_kin = model.Recording(
                sess,
                data=session['kin_data'].loc[:, kin_cols],
                identifier='kin_data',
                modality = mod_kin.Identifier
                )

        # Creating Trials
        # ----------------------------------------------------------------------------------
        for i in range(meta_session.shape[0]):
            start = meta_session.loc[i, 'StartTime']
            if i == meta_session.shape[0] - 1:
                duration = float(session['emg_data'].shape[0])/4000. - meta_session.loc[i, 'StartTime']
            else:
                duration = meta_session.loc[i + 1, 'StartTime'] - meta_session.loc[i, 'StartTime']

            if (start + duration) * session['emg_sr'] > session['emg_data'].shape[0]:
                warning = (
                        'WARNING - EMG data does not contain enough data points. Has ' +
                        '{samples:d} data points but {needed:d} are required. Skipped ' +
                        'Lift {lift:d}'
                    ).format(
                            samples = session['emg_data'].shape[0],
                            needed = int((start + duration) * session['emg_sr']),
                            lift = i
                        )
                warnings.warn(warning)
                continue

            if (start + duration) *session['eeg_sr'] > session['eeg_data'].shape[0]:
                warning = (
                        'WARNING - EEG data does not contain enough data points. Has ' +
                        '{samples:d} data points but {needed:d} are required. Skipped ' +
                        'Lift {lift:d}'
                    ).format(
                            samples = session['eeg_data'].shape[0],
                            needed = int((start + duration) * session['eeg_sr']),
                            lift = i
                        )
                warnings.warn(warning)
                continue

            t_emg = model.Trial(
                    recording=rec_emg,
                    start=start,
                    duration=duration,
                    identifier =  'emg_lift' + str(i),
                    label = weights[meta_session.loc[i, 'CurW']]# + '_' + surface[meta_session.loc[i, 'CurS']]
                )
            t_eeg = model.Trial(
                    recording=rec_eeg,
                    start=start,
                    duration=duration,
                    identifier =  'eeg_lift' + str(i),
                    label = weights[meta_session.loc[i, 'CurW']]# + '_' + surface[meta_session.loc[i, 'CurS']]
                )
            t_kin = model.Trial(
                    recording=rec_kin,
                    start=start,
                    duration=duration,
                    identifier =  'kin_lift' + str(i),
                    label = weights[meta_session.loc[i, 'CurW']]# + '_' + surface[meta_session.loc[i, 'CurS']]
                )

            if markers is not None:
                for marker in markers:
                    t_emg.add_marker((meta_session.loc[i, marker], marker))
                    t_eeg.add_marker((meta_session.loc[i, marker], marker))
                    t_kin.add_marker((meta_session.loc[i, marker], marker))
    return exp

def create_kb_for_testing():
    experiment = model.Experiment()
    so1 = model.Subject('Robert')
    experiment.put_subject(so1)

    setup = model.Setup(experiment)
    modality1 = model.Modality(setup, 15, identifier='emg')
    model.Sample(modality1, 'm1')
    model.Sample(modality1, 'm2')
    model.Sample(modality1, 'm3')
    model.Sample(modality1, 'm4')

    modality2 = model.Modality(setup, 5, identifier='pos')
    model.Sample(modality2, 'length')
    model.Sample(modality2, 'width')

    session = model.Session(experiment, setup, so1)
    emg_data = np.column_stack((
            np.arange(0,150,dtype='float'),
            np.arange(200,350,dtype='float'),
            np.arange(400,550,dtype='float'),
            np.arange(600,750,dtype='float')
            ))
    recording = model.Recording(session=session, data=emg_data,
            identifier='emg_recording', modality=modality1.Identifier)
    model.Trial(recording, 1, 2, 'trial1', label='cool')
    model.Trial(recording, 4, 1, 'trial2', label='cool')
    model.Trial(recording, 6, 3, 'trial3', label='hot')

    pos_data = np.column_stack((
            np.arange(800,850,dtype='float'),
            np.arange(900,950,dtype='float')
            ))
    recording = model.Recording(session=session, data=pos_data,
            identifier='pos_recording', modality=modality2.Identifier)
    model.Trial(recording, 1, 2, 'trial1', label='hot')
    model.Trial(recording, 4, 1, 'trial2', label='hot')
    model.Trial(recording, 6, 3, 'trial3', label='cool')
    return experiment


if __name__ == '__main__':
    e = sportKb()
    print e.recursiveToString()
    print e.getData().shape
    print len(e.getLabels())

