"""Opener of the simplified ISIC 2018 dataset"""
import os
import csv
import numpy as np
from PIL import Image


PREFIX_X = "IMG_"
SUFFIX_X = ".jpg"
PREFIX_Y = "LABEL_"
SUFFIX_Y = ".csv"
PRED_FILE = "pred.csv"

# Data Description
SIZE_X = 450
SIZE_Y = 600
SIZE_Z = 3
CLASSES = 7
N_FAKE_SAMPLES = 10


def _check_existing_files(folder, files):
    """check if files from a list of files are located in folder"""
    for fname in files:
        if not os.path.isfile(os.path.join(folder, fname)):
            raise FileNotFoundError("non existing file %s in folder %s" %
                                    (fname, folder))


def _get_files(folder):
    """return list of features and label files given a folder location (with
    the same order)"""
    # get list of features files and create associated list of label files
    X_files = [f for f in os.listdir(folder) if '.jpg' in f]
    y_files = [f.replace(PREFIX_X, PREFIX_Y).replace(SUFFIX_X, SUFFIX_Y) for f in X_files]
    # check label files exist
    try:
        _check_existing_files(folder, y_files)
    except FileNotFoundError as e:
        print(str(e))
        y_files = None
    return X_files, y_files


def get_X(folder='./data'):
    """Format and return the ISIC features data as np arrays.

    :param folder: path to the folder where all data used by the current training task have been unarchived
    :type folder: string
    :return: matrix of features
    :rtype: numpy array
    """
    print('Finding features files...')
    X_files, _ = _get_files(folder)
    print('Loading features...')
    X = []
    for f in X_files:
        image = Image.open(os.path.join(folder, f))
        X.append(np.array(image))
    return np.array(X)


def get_y(folder='./data'):
    """Format and return the ISIC labels as np arrays.
    
    :param folder: path to the folder where all data used by the current training task have been unarchived
    :type folder: string
    :return: target variable vector
    :rtype: numpy array
    """
    print('Finding label files...')
    _, y_files = _get_files(folder)
    print('Loading labels...')
    y = []
    for f in y_files:
        with open(os.path.join(folder, f)) as open_f:
            str_y = open_f.readline().split(',')
        y.append([float(yy) for yy in str_y])
    return np.array(y, dtype=np.float)


def save_pred(y_pred, folder='./pred'):
    """Save prediction in PRED_FILE in folder

    :param y_pred: predicted target variable vector
    :type y_pred: numpy array
    :param folder: path to the folder in which to save the predicted target variable vector
    :type folder: string
    :return: None
    """
    with open(os.path.join(folder, PRED_FILE), "w") as f:
        writer = csv.writer(f)
        writer.writerows(y_pred)


def get_pred(folder='./pred'):
    """Get predictions which were saved using the save_pred function

    :param folder: path to the folder where the previously predicted target variable vector has been saved
    :type folder:  string
    :return: predicted target variable vector
    :rtype: numpy array
    """
    with open(os.path.join(folder, PRED_FILE), "r") as f:
        pred_iter = csv.reader(f)
        pred = [y for y in pred_iter]
    return np.array(pred, copy=False, dtype=np.float)


def fake_X(n_samples=N_FAKE_SAMPLES):
    """Make and return the ISIC like features data as np arrays.

    :return: fake matrix of features
    :rtype: numpy array
    """
    return np.random.randint(low=0, high=256, size=(n_samples, SIZE_X, SIZE_Y, SIZE_Z)).astype('uint8')


def fake_y(n_samples=N_FAKE_SAMPLES):
    """Make and return the ISIC like labels as np arrays.

    :return: fake target variable vector
    :rtype: numpy array
    """
    return np.eye(CLASSES)[np.arange(n_samples) % CLASSES].astype('uint8')
