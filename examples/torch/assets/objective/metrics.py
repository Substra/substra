import substratools as tools


class ClassifierMetrics(tools.Metrics):
    def score(self, y_true, y_pred):
        correct = 0
        total = 0
        for predicted, labels in zip(y_pred, y_true):
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        return correct / total


if __name__ == '__main__':
    tools.metrics.execute(ClassifierMetrics())
