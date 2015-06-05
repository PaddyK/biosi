import model
import numpy as np
import pandas as pd

def createKb():
    rec1 = np.arange(100)
    rec1 = np.column_stack((rec1,rec1,rec1))
    
    rec2 = np.arange(100,200)
    rec2 = np.column_stack((rec2,rec2,rec2))
    
    rec3 = np.arange(200,300)
    rec3 = np.column_stack((rec3,rec3,rec3))
    
    data = np.row_stack((rec1,rec2,rec3))
    df = pd.DataFrame(data)
    
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
    setup = model.Setup(experiment, 10)
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
    recording = model.Recording(session = session, data = df, start = 0, duration = 100)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')
    
    # Session 2
    # ----------
    session = model.Session(experiment, setup, so2)
    recording = model.Recording(session = session, data = df, start = 100, duration = 200)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')
    
    # Session 3
    # ----------
    session = model.Session(experiment, setup, so3)
    recording = model.Recording(session = session, data = df, start = 200, duration = 300)
    model.Trial(recording, 10, 10, 'curl_simple')
    model.Trial(recording, 30, 11, 'squat')
    model.Trial(recording, 50, 12, 'curl_difficult')
    model.Trial(recording, 70, 20, 'leg_lever')
    
    return experiment
