from sklearn.metrics import recall_score

from substratools import Metrics as MetricsABC


class Metrics(MetricsABC):
    def score(self, y_true, y_pred):
        """Returns the macro-average recall

        :param y_true: actual values from test data
        :type y_true: numpy array
        :param y_true: predicted values from test data
        :type y_pred: numpy array
        :rtype: float
        """
        return recall_score(y_true.argmax(axis=1), y_pred.argmax(axis=1), average='macro')
