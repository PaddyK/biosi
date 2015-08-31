import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import os
import logging
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import emg.data as data
import model.model as model
import emg.display as display
import model.knowledgeBase as kb

import online.regression
import online.subscriber
import online.publisher
import online.sources
from online.messageclasses import ArrayMessage
import threading

logging.basicConfig(level=logging.ERROR)

def setup_sinusidal_set():
    PSI = [
            lambda x: np.sin(x),
            lambda x: np.sin(x) + 3,
            lambda x: np.sin(2*x) + 6
            ]
    X = np.arange(1000000, dtype='float').reshape(-1,1)
    transform = np.vectorize(lambda f, x: f(x), otypes=['float'])
    Z = transform(PSI, X)
    Z_corrupt = Z + np.random.normal(0, 1, Z.size).reshape(Z.shape)

    return X, Z, Z_corrupt

def setup_parabula_set(n=1000000, W=np.array([1,1,1])):
    X = np.tile(
            np.arange(-10, 10, dtype=np.float),
        10
        )
    X = np.random.random_integers(-50, 50, n)
    X = np.column_stack([X, X, X])
    Z = np.power(X, np.arange(X.shape[1]))
    Z = np.dot(Z, W).reshape(-1, 1)
    Z_corrupt = Z + np.random.normal(0, 1, Z.shape)

    return X, Z, Z_corrupt

def setup_spiral_set(n=1000, W=np.array([1,1,1])):
    fct = lambda X: np.column_stack((3 * np.cos(X), 3 * np.sin(X), 0.25 * X))
    X = np.random.rand(n) * np.random.randint(1,20,n)
    Z = fct(X)
    X = X.reshape(-1, 1)
    Z_corrupt = Z + np.random.normal(0, 1, Z.shape)
    return X, Z, Z_corrupt, fct

def plot(Z, Y):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    Y = model.predict(X)
    ax.scatter(X, Z, c='r')
    ax.scatter(X, Y, c='b')

    plt.show()

def plot3d(Z, Y):
    fig = plt.figure(1)
    ax1 = fig.add_subplot(211, projection='3d')
    ax1.scatter(Z[:,0], Z[:,1], Z[:,2], c='b')
    ax2 = fig.add_subplot(212, projection='3d')
    ax2.scatter(Y[:,0], Y[:,1], Y[:,2], c='r')
    plt.show()

def setup_emg_eeg_dataset():
    metadata = data.read_meta_file('data/P1/P1_AllLifts.mat')
    session_data = [
            data.read_session('data/P1/HS_P1_S1.mat'),
            data.read_session('data/P1/HS_P1_S2.mat'),
            data.read_session('data/P1/HS_P1_S3.mat'),
            data.read_session('data/P1/HS_P1_S4.mat'),
            data.read_session('data/P1/HS_P1_S5.mat'),
            data.read_session('data/P1/HS_P1_S6.mat')
            ]
    experiment = kb.create_emg_eeg_kb(meta=metadata, sessions=session_data, markers=None)
    dat = abs(experiment.Sessions['session_1'].Recordings['emg_data'].get_data(pandas=False))
    experiment.Sessions['session_1'].Recordings['emg_data'].set_data(dat)
    kinr = experiment.Sessions['session_1'].Recordings['kin_data']
    aligned = data.align_by_mean(experiment.Sessions['session_1'].Recordings['emg_data'],
                                 experiment.Sessions['session_1'].Recordings['kin_data'])
    cols = ['Px1 - position x sensor 1',
            'Py1 - position y sensor 1',
            'Pz1 - position z sensor 1'
            ]
    wdata, wtargets = data.windowify_labeled_data_set(
        aligned,
        kinr.get_trials_as_list(samples=cols, pandas=False),
        length=2000,
        offset=5
        )
    print 'Shape wdata before padding: {}'.format(wdata[0].shape)
    wdata = data.breze.data.padzeros(wdata, front=False)
    wtargets = data.breze.data.padzeros(wtargets, front=False)
    print 'Shape wdata: {}'.format(wdata.shape)
    X, Z, XV, ZV, XT, ZT = data.sets_for_sequence_learning(wdata, wtargets)
    print 'Shape of sets: {} {} {}'.format(X.shape, XV.shape, ZV.shape)
    return X, Z

class TestLinearRegression(object):
    def _fit(self, model, X, Z, batchsize=10, valeval=50, alpha=0.01):
        iter = 0
        best_loss = 1000000
        best_W = None
        while iter + batchsize < X.shape[0]:
            model.train(X[iter:iter+batchsize], Z[iter:iter+batchsize],alpha)
            if iter/batchsize % 50 == 0:
                loss = model.loss(X[iter:iter+batchsize], Z[iter:iter+batchsize])
                if loss < best_loss:
                    best_loss = loss
                    best_W = model._W
                print 'best loss: {} -- current loss: {}'.format(best_loss, loss)
            iter += batchsize
        model._W = best_W

    def test_parabula_set(self):
        X,Z,Z_corrupt = setup_parabula_set()
        assert Z.ndim == 2, 'Number of dimensions is incorrect'
        assert Z.shape[1] == 1, 'Z not column vector'
        assert X.shape[0] == Z.shape[0], 'Unequal first axis of X, Z'

    def test_sinusidal_set(self):
        X,Z,Z_corrupt = setup_sinusidal_set()
        assert Z.ndim == 2, 'Number of dimensions is incorrect'
        assert X.ndim == 2, 'X is not a matrix'
        assert X.shape[0] == Z.shape[0], 'Unequal first axis of X, Z'

    def test_spiral_set(self):
        X,Z,Z_corrupt,fct = setup_spiral_set()
        print('test_spiral_set: shape Z: {}'.format(Z.shape))
        assert Z.ndim == 2, 'Number of dimensions is incorrect'
        assert X.ndim == 2, 'X is not a matrix'
        assert X.shape[0] == Z.shape[0], 'Unequal first axis of X, Z'

    def test_oned_target(self,W=np.array([1,1,1])):
        X, Z, Z_corrupt = setup_parabula_set(n=100000, W=W)
        model = online.regression.LinReg(
                dim_in=X.shape[1],
                dim_out=Z.shape[1],
                dim_basis=X.shape[1],
                basis_fcts='polynomial'
                )
        self._fit(model, X, Z)

        sum_w = np.sum(W)
        sum_mw = np.sum(model._W)
        assert sum_w * 0.9 < sum_mw, 'Predicted weights out of bounds, ' + \
                'original weights are: {}, predicted weights are: {}'.format(
                        W, model._W)
        assert sum_w * 1.1 > sum_mw, 'Predicted weights out of bounds, ' + \
                'original weights are: {}, predicted weights are: {}'.format(
                        W, model._W)
        print model.loss(X, Z)

    def test_twod_target(self):
        X, Z, Z_corrupt = setup_sinusidal_set()
        model = online.regression.LinReg(
                dim_in=X.shape[1],
                dim_out=Z.shape[1],
                dim_basis=X.shape[1],
                basis_fcts='polynomial'
                )
        self._fit(model, X, Z)

        print model.loss(X, Z)

    def test_threed_target(self):
        X, Z, Z_corrupt, fct = setup_spiral_set(100000)
        model = online.regression.LinReg(
                dim_in=X.shape[1],
                dim_out=Z.shape[1],
                dim_basis=3,
                basis_fcts=fct
                )
        self._fit(model, X, Z)
        Y = model.predict(X)
        plot3d(Z[:100], Y[:100])

    def test_eeg_emg(self):
        X, Z = setup_emg_eeg_dataset()
        print 'after ste creation {}'.format(Z.shape)
        idendity = lambda X: X
        model = online.regression.LinReg(
                dim_in=X.shape[1],
                dim_out=Z.shape[1],
                dim_basis=X.shape[1],
                basis_fcts=idendity
                )
        print 'Shape X {}, Shape Z: {}'.format(X.shape, Z.shape)
        self._fit(model, X, Z, batchsize=10, alpha=0.1)
        Y = model.predict(X)
        display.predict_report(X, Y, Z, True)

    def test_learn_online(self):
        e = threading.Event()
        try:
            urlemg = 'tcp://192.168.0.16:5555'
            emgp = online.publisher.EmgPublisher(urlemg, abort=e)
            emgs = online.sources.FileSource(emgp, 4000, 'emg_data', abort=e)
            emgsub = online.subscriber.EmgSubscriber(urlemg, abort=e)
            emgiter = online.subscriber.array_iterator(ArrayMessage, emgsub)

            urlkin = 'tcp://192.168.0.16:5556'
            kinp = online.publisher.KinPublisher(urlkin, abort=e)
            kins = online.sources.FileSource(kinp, 500, 'kin_data', abort=e)
            kinsub = online.subscriber.KinSubscriber(urlkin, abort=e)
            kiniter = online.subscriber.array_iterator(ArrayMessage, kinsub)

            #sigmoid = lambda X: 1 / (1 + np.exp(X))
            identity = lambda X: X

            model = online.regression.LinReg(
                    dim_in=ArrayMessage.duration * kins.samplingrate * 5,
                    dim_out=ArrayMessage.duration * kins.samplingrate * 3,
                    dim_basis=ArrayMessage.duration * kins.samplingrate * 5,
                    basis_fcts=identity
                    )
            print 'Calculated shapes: dim_in={}, dim_out={}, dim_basis={}'.format(
                    ArrayMessage.duration * kins.samplingrate * 5,
                    ArrayMessage.duration * kins.samplingrate * 3,
                    ArrayMessage.duration * kins.samplingrate * 5
                    )
            print 'start threads'
            emgp.start()
            emgs.start()
            emgsub.start()
            kinp.start()
            kins.start()
            kinsub.start()

            count = 0
            while count < 1000:
                Z = kiniter.next().data[:, [2,7,9]]
                X = emgiter.next().data
                X_ = X.reshape(Z.shape[0], -1, X.shape[1])
                X = np.mean(X_, axis=1)
                Z = Z.flatten().reshape(1, -1)
                X = X.flatten().reshape(1, -1)
                model.train(X,Z)
                if count % 50 == 0:
                    print '{}\t\t{}'.format(count, model.loss(X, Z))
                count += 1
            e.set()
        except Exception as ex:
            e.set()
            raise ex
        e.set()

if __name__ == '__main__':
    test_online_regression()
