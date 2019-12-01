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

import numpy as np
from sklearn.model_selection import KFold

import substra

current_directory = os.path.dirname(__file__)
folds_keys_path = os.path.join(current_directory, '../folds_keys.json')

N_FOLDS = 2 
NODE_ID = 1
ALGO_NAME = "Random Forest"
DATASET_NAME = "Titanic"
OBJECTIVE_NAME = "Titanic"

with open(os.path.join(current_directory, f'../../config_node{NODE_ID}.json'), 'r') as f:
    config = json.load(f)

client = substra.Client()
client.add_profile(config['profile_name'], config['username'], config['password'],  config['url'])
client.login()

# -----------------------------------
# Retrieve objective and dataset keys
# -----------------------------------
print('Retrieving existing asset keys ...')
algo_key = [d['key'] for d in client.list_algo() if ALGO_NAME in d['name']][0]
data_manager_key = [d['key'] for d in client.list_dataset() if DATASET_NAME in
                    d['name']][0]
objective_key = [d['key'] for d in client.list_objective() if OBJECTIVE_NAME in 
                 d['name']][0]
train_data_sample_keys = client.get_dataset(data_manager_key)['trainDataSampleKeys']

# -----------------------------------
# Retrieve objective and dataset keys
# -----------------------------------
print('Generating folds...')
X = np.array(train_data_sample_keys)
kf = KFold(n_splits=N_FOLDS, shuffle=True)
folds_keys = {
    'folds': [
        {
            'train_data_sample_keys': list(X[train_index]),
            'test_data_sample_keys': list(X[test_index])
        } for train_index, test_index in kf.split(X)
    ]
}

# saving folds keys
with open(os.path.join(current_directory, folds_keys_path), 'w') as f:
    json.dump(folds_keys, f, indent=2)

print(f'Folds keys have been saved in {folds_keys_path}')

# -----------------------------------
# Submitting tasks on folds 
# -----------------------------------
print('Submitting training and testing tasks on folds...')
tag = hashlib.sha256(str(folds_keys).encode()).hexdigest()
folds_keys['tag'] = tag

for i, fold in enumerate(folds_keys['folds']):
    print(f'Adding train and test tuples for fold #{i+1}...')
    # traintuple
    traintuple = client.add_traintuple({
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': data_manager_key,
        'train_data_sample_keys': fold['train_data_sample_keys'],
        'tag': tag,
    }, exist_ok=True)
    traintuple_key = traintuple.get('key') or traintuple.get('pkhash')
    fold['traintuple_key'] = traintuple_key

    # testtuple
    testtuple = client.add_testtuple({
        'traintuple_key': traintuple_key,
        'data_manager_key': data_manager_key,
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
