import logging

import substratools as tools

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


logger = logging.getLogger(__name__)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class TorchClassifier(tools.algo.Algo):

    def _serialize_train_state(self, model, optimizer):
        """Returns single object with model and optimizer states."""
        return {
            'model': model,
            'optimizer': optimizer,
        }

    def _deserialize_train_state(self, state):
        """Returns model and optimizer states from previous ouput model train task."""
        return state['model'], state['optimizer']

    def train(self, X, y, models, rank):
        """Training task implementation."""
        net = Net()
        optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

        if rank > 0:
            model_state, optimizer_state = self._deserialize_train_state(
                models[0])

            net.load_state_dict(model_state)
            optimizer.load_state_dict(optimizer_state)

        criterion = nn.CrossEntropyLoss()

        running_loss = 0.0
        i = 0
        for inputs, labels in zip(X, y):
            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()

            i += 1
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print(f'[{i + 1:5d}] loss: {running_loss / 2000:.3f}')
                running_loss = 0.0

        return self._serialize_train_state(net.state_dict(), optimizer.state_dict())

    def predict(self, X, model):
        """Predict task implementation."""
        y_pred = []

        model_state, _ = self._deserialize_train_state(model)

        net = Net()
        net.load_state_dict(model_state)

        with torch.no_grad():
            for images in X:
                outputs = net(images)
                _, predicted = torch.max(outputs, 1)
                y_pred.append(predicted)

        return y_pred

    def save_model(self, model, path):
        torch.save(model, path)

    def load_model(self, path):
        return torch.load(path)


if __name__ == '__main__':
    tools.algo.execute(TorchClassifier())
