""" Online version of regression
"""
import numpy as np

class LinReg(object):
    """ Implements online version of linear regression according
        to ML Lecture
    """

    def __init__(self, dim_in, dim_out, transform):
        self._W = np.random.randn((dim_in, dim_out))
        """ weight matrix, columns as features, rows as classes """
        self._phi=transform

    def phi(self, X):
        return self._phi(X)

    def grad(self, X, Z):
        """ Calculates gradient for minibatch

            Args:
                X (np.ndarray): data matrix, columns are features, rows are samples
                Z (np.ndarray): targets, columns are classes, rows are samples

            Returns:
                array of shape (classes, features)
        """

        step = np.dot(self._W.T, self.phi(X).T)
        # (classes x features) * (features x samples) --> classes x samples
        step = Z - step.T
        # samples x classes - samples x classes --> samples x classes
        step = np.dot(step.T, self.phi(X).T)
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
        prediction = np.dot(self._W.T, self.phi(X).T)
        # classes x features * features x samples --> classes x samples
        return prediction.T
        # samples x classes

