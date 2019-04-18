"""Submission example with sklearn"""
# coding: utf8
import json

import numpy as np
from sklearn.linear_model import SGDClassifier

import substratools as tools


class ISICAlgo(tools.algo.Algo):

    def dump_sklearn_model(self, model):
        attr = model.__dict__
        data = {
            key: value.tolist() if isinstance(value, np.ndarray) else value
            for key, value in attr.items()
            if key[-1] == '_' and key != 'loss_function_'
        }
        return data

    def load_sklearn_model(self, data):
        model = SGDClassifier(warm_start=True, loss='log', random_state=42)
        if data is not None:
            for key, value in data.items():
                if isinstance(value, list):
                    setattr(model, key, np.array(value))
                else:
                    setattr(model, key, value)
        return model

    def train(self, X, y, models, rank=0):
        X = X.reshape(X.shape[0], -1)
        X_train = np.nan_to_num((X - np.mean(X, axis=0)) / np.std(X, axis=0))

        model = models[0] if models else None
        clf = self.load_sklearn_model(model)

        clf.fit(X_train, y.argmax(axis=1))

        y_pred = clf.predict_proba(X_train)

        return y_pred, self.dump_sklearn_model(clf)

    def predict(self, X, y, model):
        X = X.reshape(X.shape[0], -1)
        X_test = np.nan_to_num((X - np.mean(X, axis=0)) / np.std(X, axis=0))

        clf = self.load_sklearn_model(model)

        y_pred = clf.predict_proba(X_test)
        return y_pred

    def load_model(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def save_model(self, model, path):
        with open(path, 'w') as f:
            json.dump(model, f)


if __name__ == '__main__':
    tools.algo.execute(ISICAlgo())
