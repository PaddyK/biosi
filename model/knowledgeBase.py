import model
import numpy as np
import pandas as pd
import warnings

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
    modality = model.Modality(setup, 4000, 'emg')
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
        location = 'data/recording_sport.pkl',
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
    setup = model.Setup(experiment, 4000)
    modality = model.Modality(setup, 'arm')
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

def create_emg_eeg_kb(meta, session, markers=None):
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
    if meta.loc[0, 'Part'] != session['subject']:
        raise ValueError((
            'Wrong meta and session data. Meta data from subject %i and ' +
            'session data from subject %i' % (meta.loc[0, 'Part'], session['subject'])
        ))
    # Define mapping for weights and surface
    weights = {}
    weights[1] = '165g'
    weights[2] = '330g'
    weights[4] = '660g'
    surface = {}
    surface[1] = 'sandpaper'
    surface[2] = 'suede'
    surface[3] = 'silk'
    # Select data of from metadata belonging to in `session` specified session
    meta = meta.loc[meta.loc[:, 'Run'] == session['session'], :]

    # Create Experiment
    # ==================================================================================
    exp = model.Experiment()
    subj = model.Subject(session['initials'])

    # Creating Setup and Modalities
    # ==================================================================================
    setup = model.Setup(exp)
    mod_emg = model.Modality(setup, session['emg_sr'], 'emg')
    for s in session['emg_data'].columns:
        model.Sample(mod_emg, s)
    mod_eeg = model.Modality(setup, session['eeg_sr'], 'eeg')
    for s in session['eeg_data'].columns:
        model.Sample(mod_eeg, s)

    # Creating Session, Recordings and Trials
    # ==================================================================================
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

    # Creating Trials
    # ----------------------------------------------------------------------------------
    for i in range(meta.shape[0]):
        start = meta.loc[i, 'StartTime']
        duration = meta.loc[i, 'tHandStop']

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
                start=meta.loc[i, 'StartTime'],
                duration=meta.loc[i, 'tHandStop'],
                identifier =  'emg_lift' + str(i),
                label = weights[meta.loc[i, 'CurW']] + '_' + surface[meta.loc[i, 'CurS']]
            )
        t_eeg = model.Trial(
                recording=rec_eeg,
                start=meta.loc[i, 'StartTime'],
                duration=meta.loc[i, 'tHandStop'],
                identifier =  'eeg_lift' + str(i),
                label = weights[meta.loc[i, 'CurW']] + '_' + surface[meta.loc[i, 'CurS']]
            )

        for marker in markers:
            t_emg.add_marker((meta.loc[i, marker], marker))
            t_eeg.add_marker((meta.loc[i, marker], marker))
    return exp

if __name__ == '__main__':
    e = sportKb()
    print e.recursiveToString()
    print e.getData().shape
    print len(e.getLabels())

