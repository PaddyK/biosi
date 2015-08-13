import numpy as np
import matplotlib.pyplot as plt
import online.regression
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.realpath(__file__),
    os.path.pardir,
    os.path.pardir
    ))

def create_sinusidal_set():
    PSI = [
            lambda x: np.sin(x),
#            lambda x: np.sin(x) + 3,
            lambda x: np.sin(2*x) + 6
            ]
    X = np.tile(np.arange(1000000, dtype='float'), 2).reshape(1000000,2, order='F')
    transform = np.vectorize(lambda f, x: f(x), otypes=['float'])
    Z = transform(PSI, X)
    Z_corrupt = Z + np.random.normal(0, 1, Z.size).reshape(Z.shape)

    return X, Z, Z_corrupt

def create_parabula_set():
    X = np.tile(
            np.arange(-50, 50, dtype=np.float),
            100
            )
    np.random.shuffle(X)
    Z = np.add(np.add(5 * np.power(X, 2), -3 * X), 2)
    X = np.column_stack([X, X, X])
    Z_corrupt = Z + np.random.normal(0, 1, Z.shape)

    return X, Z, Z_corrupt

def test_online_regression():
    X, Z, Z_corrupt = create_parabula_set()
    model = online.regression.LinReg(
            X.shape[1],
            Z.shape[1],
            [np.tanh],
            9
            )
    batchsize = 100
    Y = None

    plt.ion()
    plt.show()

    iter = 0

    while iter + batchsize < X.shape[0]:
        if Y is None:
            Y = model.predict(X[iter:iter + batchsize])
        else:
            Y = np.concatenate([Y, model.predict(X[iter:iter + batchsize])])
        plt.clf()
        plt.plot(X[:iter + batchsize, 0], Y, c='r')
        plt.plot(X[:iter + batchsize, 0], Z[:iter + batchsize], c='g')
        plt.draw()

        model.train(X[iter:iter+batchsize], Z_corrupt[iter:iter+batchsize])
        iter += batchsize
    Y = model.predict(X, Z_corrupt)
    plt.plot(X[:,0], Y, 'r', Z, 'b')
    plt.draw()
