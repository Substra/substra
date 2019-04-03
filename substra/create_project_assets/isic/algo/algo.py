"""Submission example with sklearn"""
import os
import json
import logging
import argparse
import numpy as np
from sklearn.linear_model import SGDClassifier

import opener

# For now, logging will not be reported in Substra for security reasons
logging.basicConfig(filename='model/log_model.log', level=logging.DEBUG)


def _save_json_sklearn(model):
    """Save estimated params of a sklearn model in a json file.
    Does not work for sklearn.ensemble estimators"""
    attr = model.__dict__
    estimated_params = {key: value.tolist() if isinstance(value, np.ndarray) else value
                        for key, value in attr.items() if key[-1] == '_' and key != 'loss_function_'}
    with open('./model/model', 'w') as f:
        json.dump(estimated_params, f)


def _load_json_sklearn(inmodels):
    """ Load estimated params of a trained sklearn model from a json file"""
    model = SGDClassifier(warm_start=True, loss='log', random_state=42)
    if inmodels is not None:
        # Handle only one inmodel
        with open(os.path.join('./model', inmodels[0]), 'r') as f:
            attr = json.load(f)
        for key, value in attr.items():
            if isinstance(value, list):
                setattr(model, key, np.array(value))
            else:
                setattr(model, key, value)
    return model


def train(inmodels=None, rank=0):
    # 1. load data using opener.get_X and opener.get_y
    
    # extract data
    logging.info('Getting data')
    X_train = opener.get_X()
    y_train = opener.get_y()
    # standardize data
    X_train = X_train.reshape(X_train.shape[0], -1)
    X_train = np.nan_to_num((X_train - np.mean(X_train, axis=0)) / np.std(X_train, axis=0))

    # 2. load pre-existing models
    #    models are stored in the "./model/" folder 
    #    the inmodels param is the list of all pre-existing model filenames to use during the training
    clf = _load_json_sklearn(inmodels)

    # 3. train algorithm and produce new model
    logging.info('Fitting model')
    clf.fit(X_train, y_train.argmax(axis=1))

    # 4. save new model
    #    new model must be saved under the "./model/" folder under the filename "model" (i.e. "./model/model")
    logging.info('Saving fitted model')
    _save_json_sklearn(clf)

    # 5. save predictions made on train data (opener.get_X) using opener.save_pred
    y_pred = clf.predict_proba(X_train)
    opener.save_pred(y_pred)


def predict(inmodels=None):
    # 1. load data using opener.get_X and opener.get_y
    X_test = opener.get_X()
    X_test = X_test.reshape(X_test.shape[0], -1)
    X_test = np.nan_to_num((X_test - np.mean(X_test, axis=0)) / np.std(X_test, axis=0))

    # 2. load a model
    #    the model file name is "model" and is in the "./model/" folder (i.e. "./model/model")
    #    the inmodels param is a list containing a single element: the filename of the model to load
    clf = _load_json_sklearn(inmodels)

    # 3. save predictions made on train data (opener.get_X) using opener.save_pred
    y_pred = clf.predict_proba(X_test)
    opener.save_pred(y_pred)


def dry_run(inmodels=None):
    # 1. load data using opener.fake_X and opener.fake_y

    # extract data
    logging.info('Getting data')
    X_train = opener.fake_X()
    y_train = opener.fake_y()
    # standardize data
    X_train = X_train.reshape(X_train.shape[0], -1)
    X_train = np.nan_to_num((X_train - np.mean(X_train, axis=0)) / np.std(X_train, axis=0))

    # 2. load pre-existing models
    #    models are stored in the "./model/" folder 
    #    the inmodels param is the list of all pre-existing model filenames to use during the training
    clf = _load_json_sklearn(inmodels)

    # 3. train algorithm and produce new model
    logging.info('Fitting model')
    clf.fit(X_train, y_train.argmax(axis=1))

    # 4. save new model
    #    new model must be saved under the "./model/" folder under the filename "model" (i.e. "./model/model")
    logging.info('Saving fitted model')
    _save_json_sklearn(clf)

    # 5. save predictions made on train data (generated at step 1) using opener.save_pred
    y_pred = clf.predict_proba(X_train)
    opener.save_pred(y_pred)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true', default=False,
                        help='Launch dry run')
    parser.add_argument('-t', '--train', action='store_true', default=False,
                        help='Launch train')
    parser.add_argument('-p', '--predict', action='store_true', default=False,
                        help='Launch predict')
    parser.add_argument('-m', '--inmodels', metavar='TraintupleKey', type=str, nargs='*',
                        help='List of models from traintuplekey')
    parser.add_argument('-r', '--rank', type=int, default=0,
                        help='Rank of the fltask, if one')
    args = vars(parser.parse_args())

    logging.info(args)

    if args['train']:
        logging.info('Starting train...')
        train(inmodels=args['inmodels'], rank=args['rank'])
    elif args['predict']:
        logging.info('Starting predict...')
        predict(inmodels=args['inmodels'])
    elif args['dry_run']:
        logging.info('Starting dry run...')
        dry_run(inmodels=args['inmodels'])
    else:
        raise ValueError('task not implemented, should be either train, predict or dry-run')
