from sklearn.metrics import accuracy_score

import substratools as tools


class MnistAccuracy(tools.Metrics):
    def score(self, y_true, y_pred):
        """Returns the weighted-average f1

        :param y_true: actual values from test data
        :type y_true: pd.DataFrame
        :param y_true: predicted values from test data
        :type y_pred: pd.DataFrame
        :rtype: float
        """
        return accuracy_score(y_true, y_pred)


if __name__ == "__main__":
    tools.metrics.execute(MnistAccuracy())
