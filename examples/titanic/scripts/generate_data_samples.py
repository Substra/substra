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

"""
Script to generate data to be registered to Substra
Titanic example
"""

import os

import pandas as pd
from sklearn.model_selection import KFold, train_test_split

root_path = os.path.dirname(__file__)
asset_path = os.path.join(root_path, '../assets')

# load the full titanic example data
data = pd.read_csv(os.path.join(root_path, '../data/train.csv'))

# train / test split
train_data, test_data = train_test_split(data, test_size=0.2)

# number of data samples for the train and test sets
N_TRAIN_DATA_SAMPLES = 10
N_TEST_DATA_SAMPLES = 2

train_test_configs = [
    {
        'data': train_data,
        'n_samples': N_TRAIN_DATA_SAMPLES,
        'data_samples_dir': 'train_data_samples',
        'data_samples_content': [],
    },
    {
        'data': test_data,
        'n_samples': N_TEST_DATA_SAMPLES,
        'data_samples_dir': 'test_data_samples',
        'data_samples_content': [],
    },
]

# generate data samples
for conf in train_test_configs:
    kf = KFold(n_splits=conf['n_samples'], shuffle=True)
    splits = kf.split(conf['data'])
    for _, index in splits:
        conf['data_samples_content'].append(conf['data'].iloc[index])

# save data samples
for conf in train_test_configs:
    for i, data_sample in enumerate(conf['data_samples_content']):
        node = 1 if i < (N_TRAIN_DATA_SAMPLES/2) else 2
        filename = os.path.join(asset_path,
                                f'node_{node}',
                                conf['data_samples_dir'],
                                f'data_sample_{i}/data_sample_{i}.csv')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            data_sample.to_csv(f)
