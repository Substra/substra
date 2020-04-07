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

import os
import json

import numpy as np
from sklearn.model_selection import KFold

N_FOLDS = 4

current_directory = os.path.dirname(__file__)
assets_keys_path = os.path.join(current_directory, '../../titanic/assets_keys.json')

print(f'Loading existing asset keys from {os.path.abspath(assets_keys_path)}...')
with open(assets_keys_path, 'r') as f:
    assets_keys = json.load(f)
train_data_sample_keys = assets_keys['node_1']['train_data_sample_keys']

print('Generating folds...')
X = np.array(train_data_sample_keys)
kf = KFold(n_splits=N_FOLDS, shuffle=True)
folds = [
    {
        'train_data_sample_keys': list(X[train_index]),
        'test_data_sample_keys': list(X[test_index])
    } for train_index, test_index in kf.split(X)
]


with open(os.path.join(current_directory, '../folds_keys.json'), 'w') as f:
    json.dump({'folds': folds}, f, indent=2)

print(f'Folds keys have been saved to {os.path.abspath(assets_keys_path)}')
