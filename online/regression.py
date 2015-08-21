""" Online version of regression
"""
import numpy as np
import logging

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
            return lambda X: np.power(X, np.arange(X.shape[1]))
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
        logging.debug('LinReg.grad - Shape of transformed data: ' + \
                '{}'.format(X_.shape)
                )
        # batchsize x dim_basis
        Y = np.dot(X_, self._W) # (batchsize, dim_basis) * (dim_basis, dim_out)
        # batchsize x dimout
        D = np.subtract(Z, Y)
        # (batchsize, dim_out)
        g = np.dot(D.T, X_) # (dim_out, batchsize) * (batchsize, dim_basis)
        # (dim_out, dim_basis)
        logging.debug('LinReg.grad - Shape gradient before normalization: ' + \
                '{}'.format(g.shape)
                )
        ft_magnitudes = np.sqrt(np.sum(np.power(g, 2), axis=1)).reshape(-1, 1)
        logging.debug('LinReg.grad - magnitudes: {}'.format(ft_magnitudes))
        # Take magnitude for each output dimension
        g = np.divide(g, ft_magnitudes)
        # ``ft_magnitudes`` is row vector of dimensionality ``dim_out``
        # Therefore transpose gradient
        logging.debug('LinReg.grad - Shape gradient after normalization: ' + \
                '{}'.format(g.shape)
                )
        # (dim_out, dim_basis) / (1, dim_basis) make gradient for each feature
        # unitlength
        return g.T
        # (dim_basis, dim_out)

    def loss(self, X, Z):
        """ Let Y be the prediction
        """
        assert Z.ndim > 1, 'Target must be two dimensional (even if one dim ' + \
            'is only 1)'
        Y = self.predict(X)
        # (batchsize, dim_out)
        D = np.subtract(Z, Y)
        # (batchsize, dim_out)
        loss = np.mean(np.sum(np.power(D, 2)))
        # (n, dz) --> (dz,) --> (1,)
        return loss

    def train(self, X, Z, alpha=0.001):
        """ Performs online learning step using gradient descend on a minibatch

            Args:
                X (numpy.ndarray): Minibatch
                Z (numpy.ndarray): Targets for minibatch (rowwise,
                    one row one sample)
                alpha (float, optional): Learning Rate
        """
        assert Z.ndim > 1, 'Target must be two dimensional (even if one dim ' + \
            'is only 1)'
        logging.debug(
                'LinReg.train - Shape of weights before training: ' + \
                '{}'.format(self._W.shape)
                 )
        grad = self.grad(X, Z)
        corr = alpha * grad
        self._W = self._W + corr
        logging.debug(
                'LinReg.train - Shape of weights after ' + \
                'training: {}'.format(self._W.shape)
                )

    def predict(self, X):
        """ Predicts values for given dataset

            Args:
                X (numpy.ndarray): Data

            Returns:
                prediction, numpy.ndarray
        """
        """ Predicts value for a single vector
        """
        X_ = self._psi(X)
        logging.debug('LinReg.predict - shape of weights: {}'.format(self._W.shape))
        logging.debug('LinReg.predict - shape of weights: {}'.format(X_.shape))
        Y = np.dot(X_, self._W)
        return Y

