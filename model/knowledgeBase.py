import model
import numpy as np
import pandas as pd

def createKb(data = None):

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
    experiment.putSubject(so1)
    experiment.putSubject(so2)
    experiment.putSubject(so3)

    # Setups
    # =======
    setup = model.Setup(experiment, 1)
    modality = model.Modality(setup, 'arm')
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

def sportKb():
    experiment = model.Experiment()

    # Subjects
    # -----------------------------------------------------------------------------------
    so3 = model.Subject('subject3')
    experiment.putSubject(so3)

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

    # Session 3
    # -----------------------------------------------------------------------------------
    session = model.Session(experiment, setup, so3)
    rec = model.Recording(
        session,
        location = 'data/recording_sport.pkl',
    )
    model.Trial(rec, 0, 4, 'calm')
    model.Trial(rec, 4, 4, 'reverse_kettle1')
    model.Trial(rec, 8, 4, 'reverse_kettle2')
    model.Trial(rec, 12, 4, 'reverse_kettle3')
    model.Trial(rec, 16, 4, 'hantel1')
    model.Trial(rec, 20, 4, 'hantel2')
    model.Trial(rec, 24, 4, 'hantel3')
    model.Trial(rec, 28, 4, 'stomach_kettle1')
    model.Trial(rec, 32, 4, 'stomach_kettle2')
    model.Trial(rec, 36, 4, 'stomach_kettle3')
    model.Trial(rec, 44, 4, 'max_triceps')
    model.Trial(rec, 48, 4, 'max_flexor')
    model.Trial(rec, 52, 4, 'max_bizeps')
    model.Trial(rec, 60, 4, 'max_extensor')

    return experiment
if __name__ == '__main__':
    e = sportKb()
    print e.recursiveToString()

