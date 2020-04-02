import glob
import os
import pickle

import numpy as np
import PIL
import substratools as tools
import torch
import torchvision.transforms as transforms


class TorchDataset(torch.utils.data.Dataset):
    def __init__(self, X, y, transform=None):
        self.train = True
        self.data = X
        self.targets = y
        self.transform = transform

    def __getitem__(self, index):
        img, target = self.data[index], self.targets[index]
        img = PIL.Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        return img, target

    def __len__(self):
        return len(self.data)


class TorchOpener(tools.Opener):

    def __init__(self):
        self._X = None
        self._y = None

    def _get_Xy(self, folders):
        if self._X is not None:
            return self._X, self._y

        data = []
        labels = []

        for folder in folders:
            # code from:
            # https://pytorch.org/docs/stable/_modules/torchvision/datasets/cifar.html#CIFAR10
            # each folder should contain a single numpy file
            filepaths = glob.glob(os.path.join(folder, 'data_batch_*'))
            assert len(filepaths) == 1
            with open(filepaths[0], 'rb') as f:
                entry = pickle.load(f, encoding='latin1')

            data.append(entry['data'])
            labels.extend(entry['labels'])

        data = np.vstack(data).reshape(-1, 3, 32, 32)
        data = data.transpose((0, 2, 3, 1))

        transform = transforms.Compose(
            [transforms.ToTensor(),
             transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        shuffle = True
        trainset = TorchDataset(data, labels, transform=transform)
        trainloader = torch.utils.data.DataLoader(trainset, batch_size=4,
                                                  shuffle=shuffle, num_workers=2)

        # TODO this is very unefficient as it will load all the data in memory.
        X = []
        y = []
        for i, j in trainloader:
            X.append(i)
            y.append(j)

        self._X = X
        self._y = y
        return self._X, self._y

    def get_X(self, folders):
        X, _ = self._get_Xy(folders)
        return X

    def get_y(self, folders):
        _, y = self._get_Xy(folders)
        return y

    def save_predictions(self, y_pred, path):
        torch.save(y_pred, path)

    def get_predictions(self, path):
        return torch.load(path)

    def fake_X(self):
        raise NotImplementedError

    def fake_y(self):
        raise NotImplementedError
