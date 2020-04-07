# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
from contextlib import contextmanager
from types import SimpleNamespace

from tqdm import tqdm

import substra

default_stream_handler = logging.StreamHandler()
substra_logger = logging.getLogger('substra')
substra_logger.addHandler(default_stream_handler)


@contextmanager
def progress_bar(length):
    """Provide progress bar for for loops"""
    pg = tqdm(total=length)
    progress_handler = logging.StreamHandler(SimpleNamespace(write=lambda x: pg.write(x, end='')))
    substra_logger.removeHandler(default_stream_handler)
    substra_logger.addHandler(progress_handler)
    try:
        yield pg
    finally:
        pg.close()
        substra_logger.removeHandler(progress_handler)
        substra_logger.addHandler(default_stream_handler)


current_directory = os.path.dirname(__file__)
assets_directory = os.path.join(current_directory, '../assets/node_2')

client = substra.Client(profile_name="node-2")

DATASET = {
    'name': 'Titanic - Node 2',
    'type': 'csv',
    'data_opener': os.path.join(assets_directory, 'dataset/opener.py'),
    'description': os.path.join(assets_directory, 'dataset/description.md'),
    'permissions': {
        'public': True,
        'authorized_ids': [],
    },
}

TRAIN_DATA_SAMPLES_PATHS = [
    os.path.join(assets_directory, 'train_data_samples', path)
    for path in os.listdir(os.path.join(assets_directory, 'train_data_samples'))
]

print('Adding dataset...')
dataset_key = client.add_dataset(DATASET, exist_ok=True)['pkhash']
assert dataset_key, 'Missing data manager key'

print('Adding train data samples...')
train_data_sample_keys = []
with progress_bar(len(TRAIN_DATA_SAMPLES_PATHS)) as progress:
    for path in TRAIN_DATA_SAMPLES_PATHS:
        data_sample = client.add_data_sample({
            'data_manager_keys': [dataset_key],
            'test_only': False,
            'path': path,
        }, local=True, exist_ok=True)
        data_sample_key = data_sample['pkhash']
        train_data_sample_keys.append(data_sample_key)
        progress.update()
assert len(train_data_sample_keys), 'Missing train data samples keys'

print('Associating data samples with dataset...')
client.link_dataset_with_data_samples(
    dataset_key,
    train_data_sample_keys,
)

# Save assets keys
assets_keys_path = os.path.join(current_directory, '../assets_keys.json')
with open(assets_keys_path, 'r') as f:
    assets_keys = json.load(f)

assets_keys['node_2'] = {
    'dataset_key': dataset_key,
    'train_data_sample_keys': train_data_sample_keys,
}
with open(assets_keys_path, 'w') as f:
    json.dump(assets_keys, f, indent=2)

print(f'Node 2 assets keys have been saved to {os.path.abspath(assets_keys_path)}')
