import os
import pandas as pd
import random
import string
import numpy as np

import substratools as tools


class TitanicOpener(tools.Opener):
    def get_X(self, folders):
        data = self._get_data(folders)
        return self._get_X(data)

    def get_y(self, folders):
        data = self._get_data(folders)
        return self._get_y(data)

    def save_predictions(self, y_pred, path):
        with open(path, 'w') as f:
            y_pred.to_csv(f, index=False)

    def get_predictions(self, path):
        return pd.read_csv(path)

    def fake_X(self):
        data = self._fake_data()
        return self._get_X(data)

    def fake_y(self):
        data = self._fake_data()
        return self._get_y(data)

    @classmethod
    def _get_X(cls, data):
        return data.drop(columns=['Survived'])

    @classmethod
    def _get_y(cls, data):
        return pd.DataFrame(data=data.get('Survived'), columns=['Survived'])

    @classmethod
    def _fake_data(cls):
        N_SAMPLES = 100

        data = {
            'PassengerId': list(range(N_SAMPLES)),
            'Survived': [random.choice([True, False]) for k in range(N_SAMPLES)],
            'Pclass': [random.choice([1, 2, 3]) for k in range(N_SAMPLES)],
            'Name': ["".join(random.sample(string.ascii_letters, 10)) for k in range(N_SAMPLES)],
            'Sex': [random.choice(['male', 'female']) for k in range(N_SAMPLES)],
            'Age': [random.choice(range(7, 77)) for k in range(N_SAMPLES)],
            'SibSp': [random.choice(range(4)) for k in range(N_SAMPLES)],
            'Parch': [random.choice(range(4)) for k in range(N_SAMPLES)],
            'Ticket': ["".join(random.sample(string.ascii_letters, 10)) for k in range(N_SAMPLES)],
            'Fare': [random.choice(np.arange(15, 150, 0.01)) for k in range(N_SAMPLES)],
            'Cabin': ["".join(random.sample(string.ascii_letters, 3)) for k in range(N_SAMPLES)],
            'Embarked': [random.choice(['C', 'S', 'Q']) for k in range(N_SAMPLES)],
        }
        return pd.DataFrame(data)

    @classmethod
    def _get_data(cls, folders):
        # find csv files
        paths = []
        for folder in folders:
            paths += [os.path.join(folder, f) for f in os.listdir(folder) if f[-4:] == '.csv']

        # load data
        data = pd.DataFrame()
        for path in paths:
            data = data.append(pd.read_csv(path))

        return data
