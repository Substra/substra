from sklearn.metrics import f1_score

import substratools as tools


class MnistF1(tools.Metrics):
    def score(self, y_true, y_pred):
        """Returns the weighted-average f1

        :param y_true: actual values from test data
        :type y_true: pd.DataFrame
        :param y_true: predicted values from test data
        :type y_pred: pd.DataFrame
        :rtype: float
        """
        return f1_score(y_true, y_pred, average="weighted")


if __name__ == "__main__":
    tools.metrics.execute(MnistF1())
