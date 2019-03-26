from sklearn.metrics import recall_score


def score(y_true, y_pred):
    """returns the macro-average recall"""
    return recall_score(y_true.argmax(axis=1), y_pred.argmax(axis=1), average='macro')