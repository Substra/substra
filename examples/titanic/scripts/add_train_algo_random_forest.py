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
import zipfile

import substra

NODE_ID = 1
DATASET_NAME = "Titanic"
OBJECTIVE_NAME = "Titanic"

current_directory = os.path.dirname(__file__)
assets_directory = os.path.join(current_directory, '../assets')

with open(os.path.join(current_directory, f'../../config_node{NODE_ID}.json'), 'r') as f:
# with open(os.path.join(current_directory, '/Users/camillemarini/Desktop/config_node2.json'), 'r') as f:
    config = json.load(f)

client = substra.Client()
client.add_profile(config['profile_name'], config['username'], config['password'],  config['url'])
client.login()

ALGO_KEYS_JSON_FILENAME = 'algo_random_forest_keys.json'

ALGO = {
    'name': 'Titanic: Random Forest',
    'description': os.path.join(assets_directory,
                                'algo_random_forest/description.md'),
    'permissions': {'public': True},
}
ALGO_DOCKERFILE_FILES = [
        os.path.join(assets_directory, 'algo_random_forest/algo.py'),
        os.path.join(assets_directory, 'algo_random_forest/Dockerfile'),
]

########################################################
#       Build archive
########################################################

archive_path = os.path.join(current_directory, 'algo_random_forest.zip')
with zipfile.ZipFile(archive_path, 'w') as z:
    for filepath in ALGO_DOCKERFILE_FILES:
        z.write(filepath, arcname=os.path.basename(filepath))
ALGO['file'] = archive_path

########################################################
#       Load keys for dataset and objective
########################################################

assets_keys_path = os.path.join(current_directory, f'../assets_keys_node{NODE_ID}.json')
with open(assets_keys_path, 'r') as f:
    assets_keys = json.load(f)

########################################################
#         Add algo
########################################################

print('Adding algo...')
algo_key = client.add_algo({
    'name': ALGO['name'],
    'file': ALGO['file'],
    'description': ALGO['description'],
}, exist_ok=True)['pkhash']

########################################################
#         Add traintuples
########################################################

# Retrieve dataset and objective
data_manager_keys = [d['key'] for d in client.list_dataset() if DATASET_NAME in d['name']]
objective_key = [d['key'] for d in client.list_objective() if OBJECTIVE_NAME in 
                 d['name']][0]
traintuple_key = None
traintuple_keys = []

print('Registering traintuple...')
for data_manager_key in data_manager_keys:
    data_keys = client.get_dataset(data_manager_key)['trainDataSampleKeys']
    traintuple = client.add_traintuple({
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': data_manager_key,
        'train_data_sample_keys': data_keys,
        'in_models_keys': [traintuple_key]
    }, exist_ok=True)
    traintuple_key = traintuple.get('key') or traintuple.get('pkhash')
    print(traintuple_key)
    assert traintuple_key, 'Missing traintuple key'
    traintuple_keys.append(traintuple_key)

########################################################
#         Add testtuple
########################################################
print('Registering testtuple...')
testtuple = client.add_testtuple({
    'traintuple_key': traintuple_key
}, exist_ok=True)
testtuple_key = testtuple.get('key') or testtuple.get('pkhash')
assert testtuple_key, 'Missing testtuple key'

########################################################
#         Save keys in json
########################################################

assets_keys['algo_random_forest'] = {
    'algo_key': algo_key,
    'traintuple_key': traintuple_keys,
    'testtuple_key': testtuple_key,
}
with open(assets_keys_path, 'w') as f:
    json.dump(assets_keys, f, indent=2)

print(f'Assets keys have been saved to {os.path.abspath(assets_keys_path)}')
print('\nRun the following commands to track the status of the tuples:')
for traintuple_key in traintuple_keys:
    print(f'    substra get traintuple {traintuple_key}')
print(f'    substra get testtuple {testtuple_key}')
