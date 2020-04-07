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
import os
import uuid
import zipfile
import random

import substra

current_directory = os.path.dirname(__file__)
assets_keys_path = os.path.join(current_directory, '../../titanic/assets_keys.json')
compute_plan_keys_path = os.path.join(current_directory, '../compute_plan_keys.json')

client = substra.Client(profile_name="node-1")

print(f'Loading existing asset keys from {os.path.abspath(assets_keys_path)}...')
with open(assets_keys_path, 'r') as f:
    assets_keys = json.load(f)

node_1_train_data_sample_keys = assets_keys['node_1']['train_data_sample_keys']
node_2_train_data_sample_keys = assets_keys['node_2']['train_data_sample_keys']
objective_key = assets_keys['node_1']['objective_key']
node_1_dataset_key = assets_keys['node_1']['dataset_key']
node_2_dataset_key = assets_keys['node_2']['dataset_key']

print('Adding algo...')
algo_directory = os.path.join(current_directory, '../assets/algo_sgd')
archive_path = 'algo_sgd.zip'
with zipfile.ZipFile(archive_path, 'w') as z:
    for filename in ['algo.py', 'Dockerfile']:
        z.write(os.path.join(algo_directory, filename), arcname=filename)

algo_key = client.add_algo({
    'name': 'SGD classifier death predictor',
    'file': archive_path,
    'description': os.path.join(algo_directory, 'description.md'),
    'permissions': {
        'public': True,
        'authorized_ids': [],
    },
}, exist_ok=True)['pkhash']


print(f'Generating compute plan...')
# generate the order in which data samples will be trained on
data_keys = [(node_1_dataset_key, key) for key in node_1_train_data_sample_keys]
data_keys += [(node_2_dataset_key, key) for key in node_2_train_data_sample_keys]
random.shuffle(data_keys)
# generate compute plan tuples
traintuples = []
testtuples = []
previous_id = None
for (dataset_key, train_data_sample_key) in data_keys:
    traintuple = {
        'algo_key': algo_key,
        'data_manager_key': dataset_key,
        'train_data_sample_keys': [train_data_sample_key],
        'traintuple_id': uuid.uuid4().hex,
        'in_models_ids': [previous_id] if previous_id else [],
    }
    testtuple = {
        'objective_key': objective_key,
        'traintuple_id': traintuple['traintuple_id']
    }
    traintuples.append(traintuple)
    testtuples.append(testtuple)
    previous_id = traintuple['traintuple_id']


print('Adding compute plan...')
compute_plan = client.add_compute_plan({
    'traintuples': traintuples,
    'testtuples': testtuples,
    'composite_traintuples': [],
    'aggregatetuples': [],
})
compute_plan_id = compute_plan.get('computePlanID')

with open(compute_plan_keys_path, 'w') as f:
    json.dump(compute_plan, f, indent=2)

print(f'Compute plan keys have been saved to {os.path.abspath(compute_plan_keys_path)}')
