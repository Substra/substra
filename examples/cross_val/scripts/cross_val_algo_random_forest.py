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

import hashlib
import os
import json

import substra

current_directory = os.path.dirname(__file__)
assets_keys_path = os.path.join(current_directory, '../../titanic/assets_keys.json')
folds_keys_path = os.path.join(current_directory, '../folds_keys.json')

client = substra.Client(profile_name="node-1")

print(f'Loading existing asset keys from {os.path.abspath(assets_keys_path)}...')
with open(assets_keys_path, 'r') as f:
    assets_keys = json.load(f)

algo_key = assets_keys['algo_random_forest']['algo_key']
objective_key = assets_keys['objective_key']
dataset_key = assets_keys['dataset_key']

print(f'Loading folds keys from {os.path.abspath(folds_keys_path)}...')
with open(folds_keys_path, 'r') as f:
    folds_keys = json.load(f)

tag = hashlib.sha256(str(folds_keys).encode()).hexdigest()
folds_keys['tag'] = tag

for i, fold in enumerate(folds_keys['folds']):
    print(f'Adding train and test tuples for fold #{i+1}...')
    # traintuple
    traintuple = client.add_traintuple({
        'algo_key': algo_key,
        'data_manager_key': dataset_key,
        'train_data_sample_keys': fold['train_data_sample_keys'],
        'tag': tag,
    }, exist_ok=True)
    traintuple_key = traintuple.get('key') or traintuple.get('pkhash')
    fold['traintuple_key'] = traintuple_key

    # testtuple
    testtuple = client.add_testtuple({
        'objective_key': objective_key,
        'traintuple_key': traintuple_key,
        'data_manager_key': dataset_key,
        'test_data_sample_keys': fold['test_data_sample_keys'],
        'tag': tag,
    }, exist_ok=True)
    testtuple_key = testtuple.get('key') or testtuple.get('pkhash')
    fold['testtuple_key'] = testtuple_key

with open(folds_keys_path, 'w') as f:
    json.dump(folds_keys, f, indent=2)

print(f'Tuples keys have been saved to {os.path.abspath(folds_keys_path)}')
print('\nRun the following commands to track the status of the tuples:')
print(f'    substra list traintuple -f "traintuple:tag:{tag}"')
print(f'    substra list testtuple -f "testtuple:tag:{tag}"')
