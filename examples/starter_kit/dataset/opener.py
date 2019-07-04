def get_X(folder='./data'):
    """Get the matrix of features relevant to the current challenge

    :param folder: path to the folder where all data used by the current training task have been unarchived
    :type folder: string
    :return: matrix of features
    :rtype: python list, numpy array, etc.
    """
    pass


def get_y(folder='./data'):
    """Get the target variable vector relevant to the current challenge

    :param folder: path to the folder where all data used by the current training task have been unarchived
    :type folder: string
    :return: target variable vector
    :rtype: python list, numpy array, etc.
    """
    pass


def save_pred(y_pred, folder='./pred'):
    """Save predicted target variable vector to disk

    :param y_pred: predicted target variable vector
    :type y_pred: same type as the return type of the get_y function
    :param folder: path to the folder in which to save the predicted target variable vector
    :type folder: string
    :return: None
    """
    pass


def get_pred(folder='./pred'):
    """Load predicted target variable vector from disk

    :param folder: path to the folder where the previously predicted target variable vector has been saved
    :type folder: string
    :return: predicted target variable vector
    :rtype: same return type as the get_y function
    """
    pass


def fake_X(n_samples=10):
    """Generate a fake matrix of features for offline testing

    :param n_samples: number of samples to generate
    :type n_samples: int
    :return: fake matrix of features
    :rtype: same return type as the get_X function
    """
    pass


def fake_y(n_samples=10):
    """Generate a fake target variable vector for offline testing

    :param n_samples: number of samples to generate
    :type n_samples: int
    :return: fake target variable vector
    :rtype: same return type as the get_y function
    """
    pass
