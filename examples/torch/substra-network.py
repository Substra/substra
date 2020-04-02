#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataclasses
import os
import shutil
import tarfile
import tempfile
import uuid
import zipfile

import substra
import torchvision

DATASET_ROOT = './data'
CURRENT_DIR = os.path.dirname(__file__)
PUBLIC_PERMISSIONS = {'public': True, 'authorized_ids': []}

_CIFAR10_ARCHIVE_NAME = 'cifar-10-python.tar.gz'

# TODO format data to separate X and y?
# TODO multiple nodes example
# TODO create a click wrapper around the different commands
# TODO make this example reliable to run multiple times (could use tag to store ts)


@dataclasses.dataclass
class Context:
    profile: str = 'node1'
    assets_root: str = os.path.join(CURRENT_DIR, 'assets')

    _client: substra.Client = None

    @property
    def client(self):
        return self._client

    def initialize(self):
        self._client = substra.Client(profile_name=self.profile)
        self._client.login()
        return self


def _zip(archive_path, paths):
    with zipfile.ZipFile(archive_path, 'w') as z:
        for filepath in paths:
            z.write(filepath, arcname=os.path.basename(filepath))


def _untar(archive_path):
    destination_path = os.path.dirname(archive_path)
    with tarfile.open(archive_path) as tar:
        tar.extractall(destination_path)


def register(ctx):
    # download data
    torchvision.datasets.CIFAR10(root=DATASET_ROOT, download=True)
    _untar(os.path.join(DATASET_ROOT, _CIFAR10_ARCHIVE_NAME))

    # register dataset
    dataset_spec = {
        'name': 'CIFAR10',
        'type': 'image',
        'data_opener': os.path.join(ctx.assets_root, 'dataset/opener.py'),
        'description': os.path.join(ctx.assets_root, 'dataset/description.md'),
        'permissions': PUBLIC_PERMISSIONS,
    }
    dataset_key = ctx.client.add_dataset(dataset_spec, exist_ok=True)['pkhash']
    print(f'Dataset added: key={dataset_key}')

    # register train datasamples
    num_cifar10_batches = 5
    train_datasample_keys = []
    for i in range(num_cifar10_batches):
        datasample_path = os.path.join(
            DATASET_ROOT, 'cifar-10-batches-py', f'data_batch_{i + 1}')
        assert os.path.isfile(datasample_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            datadir = os.path.join(tmpdir, 'train_{i}/')
            os.makedirs(datadir)
            shutil.copy(datasample_path, datadir)
            datasample_spec = {
                'data_manager_keys': [dataset_key],
                'test_only': False,
                'path': datadir,
            }
            datasample_key = ctx.client.add_data_sample(
                datasample_spec, local=True, exist_ok=True)['pkhash']
            print(f'Datasample added: key={datasample_key}')
            train_datasample_keys.append(datasample_key)

    # register test datasample
    datasample_path = os.path.join(DATASET_ROOT, 'cifar-10-batches-py', 'test_batch')
    with tempfile.TemporaryDirectory() as tmpdir:
        datadir = os.path.join(tmpdir, 'test/')
        os.makedirs(datadir)
        shutil.copy(datasample_path, datadir)
        datasample_spec = {
            'data_manager_keys': [dataset_key],
            'test_only': True,
            'path': datadir,
        }
        test_datasample_key = ctx.client.add_data_sample(
            datasample_spec, local=True, exist_ok=True)['pkhash']
        print(f'Datasample added: key={test_datasample_key}')
    test_datasample_keys = [test_datasample_key]

    # link datasamples with dataset
    ctx.client.link_dataset_with_data_samples(
        dataset_key, train_datasample_keys + test_datasample_keys)

    # register objective
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, 'metrics.zip')
        objective_spec = {
            'name': 'CIFAR10',
            'description': os.path.join(ctx.assets_root, 'objective/description.md'),
            'metrics_name': 'accuracy',
            'metrics': archive_path,
            'test_data_sample_keys': None,  # TODO add test data samples
            'test_data_manager_key': dataset_key,
            'permissions': PUBLIC_PERMISSIONS,
        }
        _zip(archive_path, paths=[
            os.path.join(ctx.assets_root, 'objective/metrics.py'),
            os.path.join(ctx.assets_root, 'objective/Dockerfile'),
        ])
        objective_key = ctx.client.add_objective(objective_spec, exist_ok=True)['pkhash']
        print(f'Objective added: key={objective_key}')

    # register algo
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, 'algo.zip')
        algo_spec = {
            'name': 'CIFAR10',
            'description': os.path.join(ctx.assets_root, 'algo/description.md'),
            'file': archive_path,
            'permissions': PUBLIC_PERMISSIONS,
        }
        _zip(archive_path, paths=[
            os.path.join(ctx.assets_root, 'algo/algo.py'),
            os.path.join(ctx.assets_root, 'algo/Dockerfile'),
        ])
        algo_key = ctx.client.add_algo(algo_spec, exist_ok=True)['pkhash']
        print(f'Algo added: key={algo_key}')

    previous_traintuple_id = None

    # register compute plan
    previous_traintuple_id = None
    traintuples = []
    num_epochs = 2
    for _ in range(num_epochs):
        for key in train_datasample_keys:
            traintuple_id = uuid.uuid4().hex
            traintuple_spec = {
                'algo_key': algo_key,
                'data_manager_key': dataset_key,
                'train_data_sample_keys': [key],
                'traintuple_id': traintuple_id,
            }
            if previous_traintuple_id:
                traintuple_spec['in_models_ids'] = [previous_traintuple_id]
            traintuples.append(traintuple_spec)
            previous_traintuple_id = traintuple_id

    testtuple_spec = {
        'objective_key': objective_key,
        'traintuple_id': traintuple_id,
    }

    cp_spec = {
        'traintuples': traintuples,
        'testtuples': [testtuple_spec],
    }
    cp_id = ctx.client.add_compute_plan(cp_spec)['computePlanID']
    print(f'CP added: id={cp_id}')

    # TODO wait for the cp to be executed


if __name__ == '__main__':
    ctx = Context().initialize()
    register(ctx)
