import pandas as pd
import numpy as np
import pickle

import substratools as tools


def constant_clf(X):
    return pd.DataFrame(columns=['Survived'], data=np.zeros(len(X)), dtype=np.int64)


class TitanicAlgo(tools.algo.Algo):
    def train(self, X, y, models, rank):
        return constant_clf

    def predict(self, X, models):
        return constant_clf(X)

    def load_model(self, path):
        return constant_clf

    def save_model(self, model, path):
        with open(path, 'wb') as f:
            pickle.dump(constant_clf, f)


if __name__ == '__main__':
    tools.algo.execute(TitanicAlgo())
