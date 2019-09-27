import pandas as pd
from sklearn.externals import joblib
from sklearn.linear_model import SGDClassifier

import substratools as tools


class Algo(tools.algo.Algo):
    def _normalize_X(self, X):
        X = X.get(['Fare', 'Pclass', 'Age'])
        median_age = X.median()['Age']
        X['Age'] = X['Age'].fillna(median_age)
        return X

    def _predict_pandas(self, model, X):
        y_pred = model.predict(X)
        return pd.DataFrame(columns=['Survived'], data=y_pred)

    def train(self, X, y, models, rank):
        X = self._normalize_X(X)
        if models:
            model = models[0]
            model.warm_start = True
            model.partial_fit(X, y, classes=[0, 1])
        else:
            model = SGDClassifier(warm_start=True,
                                  learning_rate='invscaling',
                                  power_t=0.5,
                                  eta0=0.001)
            model.partial_fit(X, y, classes=[0, 1])
        y_pred = self._predict_pandas(model, X)
        return y_pred, model

    def predict(self, X, model):
        X = self._normalize_X(X)
        return self._predict_pandas(model, X)

    def load_model(self, path):
        return joblib.load(path)

    def save_model(self, model, path):
        joblib.dump(model, path)


if __name__ == '__main__':
    tools.algo.execute(Algo())
