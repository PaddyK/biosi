""" Online version of regression
"""
import numpy as np

class LinReg(object):
    """ Implements online version of linear regression according
        to ML Lecture
    """

    def __init__(self, dim_in, dim_out, batchsize, transform, polylenght):
        """ Initializes Object

            Args:
                dim_in (int): Dimensionality of input
                dim_out (int): Dimensionality of output
                batchsize (int): Size of batch
                transform (List): List of transformation functions for design
                    matrix
                polylenght (int): Length of polynomial

            Note:
                polylength has to be a multiple of legnth of transform

            Raises:
                AssertionError if polylength not multiple of length of transform
        """
        wholes, remainder = divmod(polylenght, len(trasnform))
        assert remainder == 0, 'polylength not multiple of length of ' + \
                '`transform` (online.regression.LinReg.__init__)'

        self._W = np.random.randn(dim_in, dim_out)
        """ weight matrix, columns as features, rows as classes """

        repeat = polylenght / len(transform)
        self._PSI = np.tile(np.tile(transform, repeat), batchsize).reshape(batchsize, -1)
        self._PSI = np.row_stack((
            lambda x: x,
            self._PSI
            ))
        """ Design matrix with first element being bias and the remainder
            activation functions for each element of the minibatch
        """
        self._transform = np.vectorize(lambda PSI, X: PSI(X), otypes=[object])
        """ Apply design matrix to minibatch """

    def grad(self, X, Z):
        """ Calculates gradient for minibatch

            Args:
                X (np.ndarray): data matrix, columns are features, rows are samples
                Z (np.ndarray): targets, columns are classes, rows are samples

            Returns:
                array of shape (classes, features)
        """

        print 'LinReg.grad W.T: {}, phi(X).T: {}'.format((self._W.T).shape, (self.phi(X).T).shape)
        X_head = self._transform(self._PSI, X)
        step = np.dot(self._W.T, X_head.T)
        # (classes x features) * (features x samples) --> classes x samples
        step = Z - step.T
        # samples x classes - samples x classes --> samples x classes
        print 'LinReg.grad step.T: {}, phi(X).T: {}'.format((step.T).shape, (self.phi(X).T).shape)
        step = np.dot(step.T, X_head.T)
        # classes x samples * samples x features --> classes x features
        return step.T
        # features x classes

    def train(self, X, Z, alpha=0.01):
        """ Performs online learning step using gradient descend on a minibatch

            Args:
                X (numpy.ndarray): Minibatch
                Z (numpy.ndarray): Targets for minibatch (rowwise,
                    one row one sample)
                alpha (float, optional): Learning Rate
        """
        W_head = self.grad(X, Z)
        self._W = self.W - alpha * W_head

    def predict(self, X):
        """ Predicts values for given dataset

            Args:
                X (numpy.ndarray): Data, rowwise

            Returns:
                prediction, numpy.ndarray, rowwise
        """
        X_head = self._transform(X)
        prediction = np.dot(self._W.T, X_head.T)
        # classes x features * features x samples --> classes x samples
        return prediction.T
        # samples x classes

