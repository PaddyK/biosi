import model.model
import model.knowledgeBase as kb
import emg.data
import pandas as pd
import numpy as np
import online.publisher
import online.subscriber
from online.messageclasses import ArrayMessage
import matplotlib.pyplot as plt

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

def test_alignment():
    e = kb.create_kb_for_testing()
    train_X, train_Y, val_X, val_Y, test_X, test_Y = emg.data.train_valid_test_from_modalities(
            session=e.Sessions['session0'], target_modality='pos',alignment_method='median')

    print train_X.shape
    print train_Y.shape
    print np.column_stack((train_X, train_Y))
    print ''
    print val_X.shape
    print val_Y.shape
    print ''
    print test_X.shape
    print test_Y.shape

def tc_retrieve_by_label():
    exp = kb.create_kb_for_testing()
    print exp.recursive_to_string()
    rec = exp.Sessions['session0'].Recordings['emg_recording']

    X, Z = rec.get_data_by_labels(labels=None, as_list=True, pandas=False)
    print 'len: {} - {}, types: {} - {}'.format(len(X), len(Z), type(X[0]), type(Z[0]))
    X, Z = rec.get_data_by_labels(labels=None, as_list=True, pandas=True)
    print 'len: {} - {}, types: {} - {}'.format(len(X), len(Z), type(X[0]), type(Z[0]))

    X, Z = rec.get_data_by_labels(labels=None, as_list=False, pandas=False)
    print 'shape: {} - {}, types: {} - {}'.format(
            X.shape, Z.shape, type(X), type(Z)
            )
    X, Z = rec.get_data_by_labels(labels=None, as_list=False, pandas=True)
    print 'shape: {} - {}, types: {} - {}'.format(
            X.shape, Z.shape, type(X), type(Z)
            )

def tc_nominal_windowfication():
    exp = kb.create_kb_for_testing()
    X, Z = exp.Sessions['session0'].Recordings['emg_recording'].get_data_by_labels(
            pandas=False)
    print X[0].shape, Z
    wX, wZ = emg.data.windowify_nominal_labeled_data_set(X, Z, 10)
    print type(wX), type(wZ)
    print len(wX), len(wZ)

    wX, wZ = emg.data.windowify_nominal_labeled_data_set(X, Z, 10,as_list=False)
    print type(wX), type(wZ)
    print wX.shape, wZ.shape

def tc_pub_sub_scheme():
    url = 'inproc://test'
    publisher = online.publisher.EmgPublisher(url)
    source = online.sources.FileSource(publisher, 4000)
    subscriber = online.subscriber.EmgSubscriber(url)

    url = 'inproc://test'
    print 'start source'
    source.start()
    print 'start publisher'
    publisher.start()
    print 'start subscriber'
    subscriber.start()

    plt.ion()
    plt.show()
    set = None
    start = 0
    for arrmsg in online.subscriber.array_iterator(ArrayMessage, subscriber):
        msgdata = arrmsg.data
        if set is None:
            set = msgdata

        if set.shape[0] > 16000:
            set = set[1000:]
            start += 0.25
        set = np.row_stack((set, msgdata))
        x = np.arange(set.shape[0])/4000. + start

        plt.clf()
        plt.ylim(-2,2)
        plt.plot(x, set)
        plt.draw()

if __name__ == '__main__':
    tc_pub_sub_scheme()
