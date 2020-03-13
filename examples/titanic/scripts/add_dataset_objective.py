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
import zipfile
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
assets_directory = os.path.join(current_directory, '../assets')

client = substra.Client(profile_name="node-1")

DATASET = {
    'name': 'Titanic',
    'type': 'csv',
    'data_opener': os.path.join(assets_directory, 'dataset/opener.py'),
    'description': os.path.join(assets_directory, 'dataset/description.md'),
}

TEST_DATA_SAMPLES_PATHS = [
    os.path.join(assets_directory, 'test_data_samples', path)
    for path in os.listdir(os.path.join(assets_directory, 'test_data_samples'))
]

TRAIN_DATA_SAMPLES_PATHS = [
    os.path.join(assets_directory, 'train_data_samples', path)
    for path in os.listdir(os.path.join(assets_directory, 'train_data_samples'))
]

OBJECTIVE = {
    'name': 'Titanic: Machine Learning From Disaster',
    'description': os.path.join(assets_directory, 'objective/description.md'),
    'metrics_name': 'accuracy',
    'metrics': os.path.join(assets_directory, 'objective/metrics.zip'),
}
METRICS_DOCKERFILE_FILES = [
    os.path.join(assets_directory, 'objective/metrics.py'),
    os.path.join(assets_directory, 'objective/Dockerfile')
]

archive_path = OBJECTIVE['metrics']
with zipfile.ZipFile(archive_path, 'w') as z:
    for filepath in METRICS_DOCKERFILE_FILES:
        z.write(filepath, arcname=os.path.basename(filepath))


print('Adding dataset...')
dataset_key = client.add_dataset(DATASET, exist_ok=True)['pkhash']
assert dataset_key, 'Missing data manager key'

train_data_sample_keys = []
test_data_sample_keys = []
data_samples_configs = (
    {
        'message': 'Adding train data samples...',
        'paths': TRAIN_DATA_SAMPLES_PATHS,
        'test_only': False,
        'data_sample_keys': train_data_sample_keys,
        'missing_message': 'Missing train data samples keys',
    },
    {
        'message': 'Adding test data samples...',
        'paths': TEST_DATA_SAMPLES_PATHS,
        'test_only': True,
        'data_sample_keys': test_data_sample_keys,
        'missing_message': 'Missing test data samples keys'
    },
)
for conf in data_samples_configs:
    print(conf['message'])
    with progress_bar(len(conf['paths'])) as progress:
        for path in conf['paths']:
            data_sample = client.add_data_sample({
                'data_manager_keys': [dataset_key],
                'test_only': conf['test_only'],
                'path': path,
            }, local=True, exist_ok=True)
            data_sample_key = data_sample['pkhash']
            conf['data_sample_keys'].append(data_sample_key)
            progress.update()
    assert len(conf['data_sample_keys']), conf['missing_message']

print('Associating data samples with dataset...')
client.link_dataset_with_data_samples(
    dataset_key,
    train_data_sample_keys + test_data_sample_keys,
)

print('Adding objective...')
objective_key = client.add_objective({
    'name': OBJECTIVE['name'],
    'description': OBJECTIVE['description'],
    'metrics_name': OBJECTIVE['metrics_name'],
    'metrics': OBJECTIVE['metrics'],
    'test_data_sample_keys': test_data_sample_keys,
    'test_data_manager_key': dataset_key,
}, exist_ok=True)['pkhash']
assert objective_key, 'Missing objective key'

# Save assets keys
assets_keys = {
    'dataset_key': dataset_key,
    'objective_key': objective_key,
    'train_data_sample_keys': train_data_sample_keys,
    'test_data_sample_keys': test_data_sample_keys,
}
assets_keys_path = os.path.join(current_directory, '../assets_keys.json')
with open(assets_keys_path, 'w') as f:
    json.dump(assets_keys, f, indent=2)

print(f'Assets keys have been saved to {os.path.abspath(assets_keys_path)}')
