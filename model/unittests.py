import model
import knowledgeBase as kb
import pandas as pd
import numpy as np

def tcBuildModel():
    exp = kb.createKb()
    print exp.recursiveToString()

def tcDataRetrieval():
    exp = kb.createKb()

    print '\nTrial0\n-------'
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_simple'].get_data()
    print '\nTrial1\n-------'
    print exp.Sessions['session0'].Recordings['recording0'].Trials['squat'].get_data()
    print '\nTrial2\n-------'
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_difficult'].get_data()
    print '\nTrial3\n-------'
    print exp.Sessions['session0'].Recordings['recording0'].Trials['leg_lever'].get_data()
    print '\nRecording\n-------'
    print exp.Sessions['session0'].Recordings['recording0'].get_data()
    print '\nSession\n-------'
    print exp.Sessions['session0'].get_data()

    print '\nTrial0\n-------'
    print exp.Sessions['session1'].Recordings['recording0'].Trials['curl_simple'].get_data()
    print '\nTrial1\n-------'
    print exp.Sessions['session1'].Recordings['recording0'].Trials['squat'].get_data()
    print '\nTrial2\n-------'
    print exp.Sessions['session1'].Recordings['recording0'].Trials['curl_difficult'].get_data()
    print '\nTrial3\n-------'
    print exp.Sessions['session1'].Recordings['recording0'].Trials['leg_lever'].get_data()
    print '\nRecording\n-------'
    print exp.Sessions['session1'].Recordings['recording0'].get_data()

    print '\nTrial0\n-------'
    print exp.Sessions['session1'].Recordings['recording1'].Trials['curl_simple2'].get_data()
    print '\nTrial1\n-------'
    print exp.Sessions['session1'].Recordings['recording1'].Trials['squat2'].get_data()
    print '\nTrial2\n-------'
    print exp.Sessions['session1'].Recordings['recording1'].Trials['curl_difficult2'].get_data()
    print '\nTrial3\n-------'
    print exp.Sessions['session1'].Recordings['recording1'].Trials['leg_lever2'].get_data()
    print '\nRecording\n-------'
    print exp.Sessions['session1'].Recordings['recording1'].get_data()
    print '\nSession\n-------'
    print exp.Sessions['session1'].get_data()

    print '\nTrial0\n-------'
    print exp.Sessions['session2'].Recordings['recording0'].Trials['curl_simple'].get_data()
    print '\nTrial1\n-------'
    print exp.Sessions['session2'].Recordings['recording0'].Trials['squat'].get_data()
    print '\nTrial2\n-------'
    print exp.Sessions['session2'].Recordings['recording0'].Trials['curl_difficult'].get_data()
    print '\nTrial3\n-------'
    print exp.Sessions['session2'].Recordings['recording0'].Trials['leg_lever'].get_data()
    print '\nRecording\n-------'
    print exp.Sessions['session2'].Recordings['recording0'].get_data()
    print '\nSession\n-------'
    print exp.Sessions['session2'].get_data()

def tcDataAssignment():
    rec1 = np.arange(100, dtype = 'float')
    rec1 = np.column_stack((rec1,rec1,rec1))

    rec2 = np.arange(100,200, dtype = 'float')
    rec2 = np.column_stack((rec2,rec2,rec2))

    rec3 = np.arange(200,300, dtype = 'float')
    rec3 = np.column_stack((rec3,rec3,rec3))

    data = np.row_stack((rec1,rec2,rec3))
    print data.dtype
    exp = kb.createKb(data)
    
    print '\nTrial0\n-------'
    d = pd.DataFrame(np.arange(50.5,80.5, dtype = 'float').reshape(10,3), dtype = 'float')
    print d.dtypes
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_simple'].get_data()
    exp.Sessions['session0'].Recordings['recording0'].Trials['curl_simple'].set_data(d)
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_simple'].get_data()
    print data

    print '\nTrial1\n-------'
    d = pd.DataFrame(np.arange(200.5,233.5, dtype = 'float').reshape(11,3), dtype = 'float')
    exp.Sessions['session0'].Recordings['recording0'].Trials['squat'].set_data(d)
    print exp.Sessions['session0'].Recordings['recording0'].Trials['squat'].get_data()
    print data
    
    print '\nTrial2\n-------'
    d = pd.DataFrame(np.arange(400.5,436.5, dtype = 'float').reshape(12,3), dtype = 'float')
    exp.Sessions['session0'].Recordings['recording0'].Trials['curl_difficult'].set_data(d)
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_difficult'].get_data()
    print data
    
    print '\nTrial3\n-------'
    d = pd.DataFrame(np.arange(600.5,660.5, dtype = 'float').reshape(20,3), dtype = 'float')
    exp.Sessions['session0'].Recordings['recording0'].Trials['leg_lever'].set_data(d)
    print exp.Sessions['session0'].Recordings['recording0'].Trials['leg_lever'].get_data()
    print data
   
    print 'Recording - relevant data'
    print '~~~~~~~~~~~~~~~~~~~~~~~~~'
    print exp.Sessions['session0'].Recordings['recording0'].get_data()
    print 'Recording - all data'
    print '~~~~~~~~~~~~~~~~~~~~~~~~~'
    print exp.Sessions['session0'].Recordings['recording0'].get_all_data()

    print '\nRecording\n-------'
    exp.Sessions['session0'].Recordings['recording0'].set_data(pd.DataFrame(
        np.arange(1000,1159, dtype = 'float').reshape(53,3)
    ))
    print exp.Sessions['session0'].Recordings['recording0'].get_data()
    print exp.Sessions['session0'].Recordings['recording0'].get_all_data()
    print exp.Sessions['session0'].Recordings['recording0'].Trials['curl_simple'].get_data()
    print data
    
    print '\nSession\n-------'
    exp.Sessions['session0'].set_data(pd.DataFrame(
        np.arange(9000.5,9159.5, dtype = 'float').reshape(53,3), dtype = 'float'
    ))
    print exp.Sessions['session0'].get_data()
    print exp.Sessions['session0'].Recordings['recording0'].get_all_data()
    print exp.Sessions['session0'].Recordings['recording0'].get_data()

    print '\nSession\n-------'
    exp.Sessions['session1'].set_data(pd.DataFrame(
        np.arange(500.5,818.5, dtype = 'float').reshape(106,3), dtype = 'float'
    ))

    print exp.Sessions['session1'].get_all_data()
    print exp.Sessions['session1'].get_data()
    print exp.Sessions['session1'].Recordings['recording0'].get_all_data()
    print exp.Sessions['session1'].Recordings['recording0'].get_data()
    print exp.Sessions['session1'].Recordings['recording1'].get_all_data()
    print exp.Sessions['session1'].Recordings['recording1'].get_data()
    
def tcReadFromFile():
    path = '/home/patrick/interdiciplinary_project/data/recording_sport.pkl'
#    path = '/home/patrick/interdiciplinary_project/data/recording_sport.txt'
    data = model.DataController()
#    pd = data.readDataFromText(path)
    pd = data.read_pickled_data(path)
    print pd
    print pd.dtypes

def tcLoadByLabel():
    e = kb.sportKb()
    lst = ['hantel', 'reverse_kettle']
    data, labels = e.get_data_by_labels(lst)
    print data.shape
    print len(labels)
    print data

if __name__ == '__main__':
    tcLoadByLabel()
