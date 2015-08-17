import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import online.regression

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
            np.arange(-10, 10, dtype=np.float),
            10
            )
    X = np.random.random_integers(-50, 50, 1000000)
    np.random.shuffle(X)
    Z = np.add(np.add(5 * np.power(X, 2), -3 * X), 2)
    Z = Z.reshape(-1, 1)
    X = np.column_stack([X, X, X])
    Z_corrupt = Z + np.random.normal(0, 1, Z.shape)

    return X, Z, Z_corrupt

def test_online_regression():
    X, Z, Z_corrupt = create_parabula_set()
    dim_out = 1 if Z.ndim == 1 else Z.shape[1]
    model = online.regression.LinReg(
            dim_in=X.shape[1],
            dim_out=dim_out,
            dim_basis=X.shape[1],
            basis_fcts='polynomial'
            )
    batchsize = 10
    Y = None

    iter = 0

    while iter + batchsize < X.shape[0]:
        model.train(X[iter:iter+batchsize], Z[iter:iter+batchsize],alpha=0.001)
        print model.loss(X[iter:iter+batchsize], Z[iter:iter+batchsize])
        iter += batchsize
    fig = plt.figure()
    ax = fig.add_subplot(111)

    Y = model.predict(X[:1000])
    ax.scatter(X[:1000,0], Z[:1000], c='r')
    ax.scatter(X[:1000, 0], Y, c='b')

    plt.show()
    print model._W
    print model.loss(X, Z)

if __name__ == '__main__':
    test_online_regression()
