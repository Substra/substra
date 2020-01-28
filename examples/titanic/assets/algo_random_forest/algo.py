import re

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

import numpy as np

import substratools as tools


class Algo(tools.algo.Algo):

    def _normalize_X(self, X):
        # Relatives
        X['relatives'] = X['SibSp'] + X['Parch']
        X.loc[X['relatives'] > 0, 'not_alone'] = 0
        X.loc[X['relatives'] == 0, 'not_alone'] = 1
        X['not_alone'] = X['not_alone'].astype(int)

        # Passenger ID
        X = X.drop(['PassengerId'], axis=1)

        # Cabin
        deck = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "U": 8}
        X['Cabin'] = X['Cabin'].fillna("U0")
        X['Deck'] = X['Cabin'].map(
            lambda x: re.compile("([a-zA-Z]+)").search(x).group())
        X['Deck'] = X['Deck'].map(deck)
        X['Deck'] = X['Deck'].fillna(0)
        X['Deck'] = X['Deck'].astype(int)
        X = X.drop(['Cabin'], axis=1)

        # Age
        mean = X["Age"].mean()
        std = X["Age"].std()
        is_null = X["Age"].isnull().sum()
        # compute random numbers between the mean, std and is_null
        rand_age = np.random.randint(mean - std, mean + std, size=is_null)
        # fill NaN values in Age column with random values generated
        age_slice = X["Age"].copy()
        age_slice[np.isnan(age_slice)] = rand_age
        X["Age"] = age_slice
        X["Age"] = X["Age"].astype(int)
        # make Age into a category
        X['Age'] = X['Age'].astype(int)
        X.loc[X['Age'] <= 11, 'Age'] = 0
        X.loc[(X['Age'] > 11) & (X['Age'] <= 18), 'Age'] = 1
        X.loc[(X['Age'] > 18) & (X['Age'] <= 22), 'Age'] = 2
        X.loc[(X['Age'] > 22) & (X['Age'] <= 27), 'Age'] = 3
        X.loc[(X['Age'] > 27) & (X['Age'] <= 33), 'Age'] = 4
        X.loc[(X['Age'] > 33) & (X['Age'] <= 40), 'Age'] = 5
        X.loc[(X['Age'] > 40) & (X['Age'] <= 66), 'Age'] = 6
        X.loc[X['Age'] > 66, 'Age'] = 6
        # create Age_Class feature
        X['Age_Class'] = X['Age'] * X['Pclass']

        # Embarked
        ports = {"S": 0, "C": 1, "Q": 2}
        X['Embarked'] = X['Embarked'].fillna('S')
        X['Embarked'] = X['Embarked'].map(ports)

        # Fare
        X['Fare'] = X['Fare'].fillna(0)
        X['Fare'] = X['Fare'].astype(int)
        # make Fare into a category
        X.loc[X['Fare'] <= 7.91, 'Fare'] = 0
        X.loc[(X['Fare'] > 7.91) & (X['Fare'] <= 14.454), 'Fare'] = 1
        X.loc[(X['Fare'] > 14.454) & (X['Fare'] <= 31), 'Fare'] = 2
        X.loc[(X['Fare'] > 31) & (X['Fare'] <= 99), 'Fare'] = 3
        X.loc[(X['Fare'] > 99) & (X['Fare'] <= 250), 'Fare'] = 4
        X.loc[X['Fare'] > 250, 'Fare'] = 5
        X['Fare'] = X['Fare'].astype(int)
        # create Fare_Per_Person feature
        X['Fare_Per_Person'] = X['Fare'] / (X['relatives'] + 1)
        X['Fare_Per_Person'] = X['Fare_Per_Person'].astype(int)

        # Name
        titles = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
        # extract titles
        X['Title'] = X.Name.str.extract(r' ([A-Za-z]+)\.', expand=False)
        # replace titles with a more common title or as Rare
        X['Title'] = X['Title'].replace(
            ['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr',
             'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        X['Title'] = X['Title'].replace('Mlle', 'Miss')
        X['Title'] = X['Title'].replace('Ms', 'Miss')
        X['Title'] = X['Title'].replace('Mme', 'Mrs')
        # convert titles into numbers
        X['Title'] = X['Title'].map(titles)
        # filling NaN with 0, to get safe
        X['Title'] = X['Title'].fillna(0)
        X = X.drop(['Name'], axis=1)

        # Sex
        genders = {"male": 0, "female": 1}
        X['Sex'] = X['Sex'].map(genders)

        # Ticket
        X = X.drop(['Ticket'], axis=1)

        # Drop non relevant features
        X = X.drop("not_alone", axis=1)
        X = X.drop("Parch", axis=1)

        return X

    def _predict_pandas(self, model, X):
        y_pred = model.predict(X)
        return pd.DataFrame(columns=['Survived'], data=y_pred)

    def train(self, X, y, models, rank):
        X = self._normalize_X(X)

        # the following RFC hyperparameters were determined using:
        # >>> param_grid = {"criterion": ["gini", "entropy"],
        #                   "min_samples_leaf": [1, 5, 10, 25, 50, 70],
        #                   "min_samples_split": [2, 4, 10, 12, 16, 18, 25, 35],
        #                   "n_estimators": [100, 400, 700, 1000, 1500]}
        # >>> rf = RandomForestClassifier(n_estimators=100, max_features='auto', oob_score=True,
        #                                 random_state=1, n_jobs=-1)
        # >>>,clf = GridSearchCV(estimator=rf, param_grid=param_grid, n_jobs=-1)

        # Random Forest
        random_forest = RandomForestClassifier(criterion="gini",
                                               min_samples_leaf=1,
                                               min_samples_split=10,
                                               n_estimators=100,
                                               max_features='auto',
                                               oob_score=True,
                                               random_state=1,
                                               n_jobs=-1)
        random_forest.fit(X, y)

        return random_forest

    def predict(self, X, model):
        X = self._normalize_X(X)
        return self._predict_pandas(model, X)

    def load_model(self, path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def save_model(self, model, path):
        with open(path, 'wb') as f:
            pickle.dump(model, f)


if __name__ == '__main__':
    tools.algo.execute(Algo())
