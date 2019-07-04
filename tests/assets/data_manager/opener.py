"""Opener of the ISIC 2018 dataset"""
import os
import csv
import numpy as np
from PIL import Image


PREFIX_X = "IMG_"
SUFFIX_X = ".jpg"
PREFIX_Y = "LABEL_"
SUFFIX_Y = ".csv"
PRED_FILE = "pred.csv"


def check_existing_files(folder, files):
    """check if files from a list of files are located in folder"""
    for fname in files:
        if not os.path.isfile(os.path.join(folder, fname)):
            raise FileNotFoundError("non existing file %s in folder %s" %
                                    (fname, folder))


def get_files(folder):
    """return list of features and label files given a folder location (with
    the same order)"""
    # get list of features files and create associated list of label files
    X_files = [f for f in os.listdir(folder) if '.jpg' in f]
    y_files = [f.replace(PREFIX_X, PREFIX_Y).replace(SUFFIX_X, SUFFIX_Y) for f in X_files]
    # check label files exist
    try:
        check_existing_files(folder, y_files)
    except FileNotFoundError as e:
        print(str(e))
        y_files = None
    return X_files, y_files


def get_X(folder):
    """Format and return the ISIC features data as np arrays."""
    print('Finding features files...')
    X_files, _ = get_files(folder)
    print('Loading features...')
    X = []
    for f in X_files:
        image = Image.open(os.path.join(folder, f))
        X.append(np.array(image))
    return np.array(X)


def get_y(folder):
    """Format and return the ISIC labels as np arrays."""
    print('Finding label files...')
    _, y_files = get_files(folder)
    print('Loading labels...')
    y = []
    for f in y_files:
        with open(os.path.join(folder, f)) as open_f:
            str_y = open_f.readline().split(',')
        y.append([float(yy) for yy in str_y])
    return np.array(y)


def save_pred(y_pred, folder):
    """Save prediction in PRED_FILE in folder"""
    with open(os.path.join(folder, PRED_FILE), "w") as f:
        writer = csv.writer(f)
        writer.writerows(y_pred)


def get_pred(folder):
    """Get predictions which were saved using the save_pred function"""
    with open(os.path.join(folder, PRED_FILE), "r") as f:
        pred_iter = csv.reader(f)
        pred = [y for y in pred_iter]

    return np.array(pred, copy=False)
