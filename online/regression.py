""" Online version of regression
"""
import numpy as np

class LinReg(object):
    """ Implements online version of linear regression according
        to ML Lecture
    """

    def __init__(self, dim_in, dim_out, dim_basis, basis_fcts):
        """ Initializes Object

            Args:
                dim_in (int): Dimensionality of input
                dim_out (int): Dimensionality of output
                dim_basis (int): Dimensionality of vector of basis functions
                basis_fcts (array): column array of transfer functions (first
                    element has to be one) with as many rows as dim_in

            Note:
                The basis function will be given a matrix where samples are
                stored rowwise. The basis function must return a Matrix with
                the same number of rows, columns may differ

            Available Basis Functions:
                tanh: Apply hyperbolic tangent to each element of x_{i}
                sigmoid: Apply sigmoid to each element of x_{i}
                polynomial: Raise each feature to power according to position
                    that is first feature to power 0, nth feature to power n-1
        """
        self._W = np.random.randn(dim_basis, dim_out)
        """ weight matrix, columns as features due to activation functions, rows as classes """
        self._psi = self._register_basis_function(basis_fcts)
        """ Apply respective transfer function to each feature """

    def _register_basis_function(self, basis_fcts):
        """ Checks if one of supported keywoards and creates fct accordingly
        """
        if basis_fcts == 'tanh':
            return np.tanh
        elif basis_fcts == 'sigmoid':
            return lambda X: np.divide(1., np.add(1., np.exp(-X)))
        elif basis_fcts == 'polynomial':
            return lambda X, order: np.power(X, order)
        else:
            return basis_fcts

    def grad(self, X, Z):
        """ Calculates gradient for minibatch

            Args:
                X (np.ndarray): data matrix, columns are features, rows are samples
                Z (np.ndarray): targets, columns are classes, rows are samples

            Returns:
                array of shape (classes, features)
        """
        X_ = self._psi(X)
        g = np.mean(np.dot(np.dot(X_, W).T, X_), axis=1)
        # [(n x db)*(db x dz)] --> (n, dz) --> (dz, n)*(n, db) --> (dz, n) --> (dz, 1)
        return g

    def loss(self, X, Z):
        """ Let Y be the prediction
        """
        Y = self.predict(X, Z)
        # (n, dz)
        D = np.subtract(Z, Y)
        # (n, dz)
        loss = np.mean(np.sum(np.power(D, 2), axis=0))
        # (n, dz) --> (dz,) --> (1,)
        return np.mean(np.dot(self.predict(X,Z).T, Z))

    def train(self, X, Z, alpha=0.01):
        """ Performs online learning step using gradient descend on a minibatch

            Args:
                X (numpy.ndarray): Minibatch
                Z (numpy.ndarray): Targets for minibatch (rowwise,
                    one row one sample)
                alpha (float, optional): Learning Rate
        """
        grad = self.grad(X, Z)
        self._W = self.W - alpha * grad

    def predict(self, X):
        """ Predicts values for given dataset

            Args:
                X (numpy.ndarray): Data

            Returns:
                prediction, numpy.ndarray
        """
        """ Predicts value for a single vector
        """
        Y = np.dot(self._psi(X), W)
        return Y

