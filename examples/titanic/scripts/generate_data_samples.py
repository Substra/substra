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
import shutil
import time

import pandas as pd
from sklearn.model_selection import KFold, train_test_split

root_path = os.path.dirname(__file__)
asset_path = os.path.join(root_path, '../assets')

# load the full titanic example data
data = pd.read_csv(os.path.join(root_path, '../data/train.csv'))

# train / test split
train_data, test_data = train_test_split(data, test_size=0.2)

# number of nodes, of data samples for a train set in a node and for the test set
N_NODES = 2
N_TRAIN_DATA_SAMPLES = 5 
N_TEST_DATA_SAMPLES = 2

train_test_configs = [
    {
        'data': train_data,
        'n_samples': N_TRAIN_DATA_SAMPLES * N_NODES,
        'data_samples_root': os.path.join(asset_path, 'train_data_samples'),
        'data_samples_content': [],
    },
    {
        'data': test_data,
        'n_samples': N_TEST_DATA_SAMPLES,
        'data_samples_root': os.path.join(asset_path, 'test_data_samples'),
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
        i_node = i // N_TRAIN_DATA_SAMPLES
        filename = os.path.join(f"{conf['data_samples_root']}_node{i_node}",
                                f'data_sample_{i % N_NODES}/data_sample_{i_node}.csv')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            data_sample.to_csv(f)

# create dataset opener and description
for i_node in range(N_NODES):
    filedir = os.path.join(asset_path, f'dataset')
    node_filedir = f'{filedir}_node{i_node}'
    try:
        shutil.copytree(filedir, node_filedir)
    except FileExistsError:
        print(f'assets for {node_filedir} already exist')
    else:
        with open(os.path.join(node_filedir, 'opener.py'), 'a+') as f:                                                         
            f.write(f'# opener of node {i_node} - {time.time()}')
        with open(os.path.join(node_filedir, 'description.md'), 'a+') as f:
            f.write(f'Dataset belongs to node {i_node} - {time.time()}')
