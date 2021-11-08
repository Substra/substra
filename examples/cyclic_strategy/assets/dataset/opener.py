import os
import pandas as pd
import random

import substratools as tools


class MnistOpener(tools.Opener):
    def get_X(self, folders):
        data = self._get_data(folders)
        return self._get_X(data)

    def get_y(self, folders):
        data = self._get_data(folders)
        return self._get_y(data)

    def save_predictions(self, y_pred, path):
        with open(path, "w") as f:
            y_pred.to_csv(f, index=False)

    def get_predictions(self, path):
        return pd.read_csv(path)

    def fake_X(self, n_samples=None):
        data = self._fake_data(n_samples)
        return self._get_X(data)

    def fake_y(self, n_samples=None):
        data = self._fake_data(n_samples)
        return self._get_y(data)

    @classmethod
    def _get_X(cls, data):
        return data.drop(columns=["target"])

    @classmethod
    def _get_y(cls, data):
        return pd.DataFrame(data=data.get("target"), columns=["target"])

    @classmethod
    def _fake_data(cls, n_samples=None):
        N_SAMPLES = n_samples if n_samples and n_samples <= 100 else 100

        data = pd.DataFrame(
            [[random.choices(range(17))[0] for i in range(64)] for j in range(N_SAMPLES)],
            columns=[f"pixel_{k}" for k in range(64)],
        )
        data.loc[:, "target"] = [random.choices(range(10))[0] for i in range(N_SAMPLES)]

        return data

    @classmethod
    def _get_data(cls, folders):
        # find csv files
        paths = []
        for folder in folders:
            paths += [os.path.join(folder, f) for f in os.listdir(folder) if f[-4:] == ".csv"]

        # load data
        data = pd.DataFrame()
        for path in paths:
            data = data.append(pd.read_csv(path, index_col=0))

        return data
