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

import substra

current_directory = os.path.dirname(__file__)
compute_plan_keys_path = os.path.join(current_directory, '../compute_plan_keys.json')

NODE_ID = 1
DATASET_NAME = "Titanic"
OBJECTIVE_NAME = "Titanic"

with open(os.path.join(current_directory, f'../../config_node{NODE_ID}.json'), 'r') as f:
    config = json.load(f)

client = substra.Client()
client.add_profile(config['profile_name'], config['username'], config['password'],  config['url'])
client.login()


# Retrieve objective and dataset keys
data_manager_keys = [d['key'] for d in client.list_dataset() if DATASET_NAME in d['name']]
objective_key = [d['key'] for d in client.list_objective() if OBJECTIVE_NAME in 
                 d['name']][0]
train_data_sample_keys = []
for data_manager_key in data_manager_keys:
    train_data_sample_keys.append(client.get_dataset(data_manager_key)['trainDataSampleKeys'])
# Create data batches: one sample of Node0, one of Node 1, onde of Node 0, ....
data_batches = []
n_batch = max([len(tds) for tds in train_data_sample_keys])
for i in range(n_batch):
    for j, data_manager_key in enumerate(data_manager_keys):
        try:
            data_batches.append([data_manager_key, train_data_sample_keys[j]])
        except IndexError:
            pass


print('Adding algo...')
algo_directory = os.path.join(current_directory, '../assets/algo_sgd')
archive_path = 'algo_sgd.zip'
with zipfile.ZipFile(archive_path, 'w') as z:
    for filename in ['algo.py', 'Dockerfile']:
        z.write(os.path.join(algo_directory, filename), arcname=filename)

algo_key = client.add_algo({
    'name': 'SGD classifier death predictor',
    'file': archive_path,
    'description': os.path.join(algo_directory, 'description.md')
}, exist_ok=True)['pkhash']


print(f'Generating compute plan...')
traintuples = []
testtuples = []
previous_id = None
# for data_btrain_data_sample_key in train_data_sample_keys:
for data_batch in data_batches:
    traintuple = {
        'data_manager_key': data_batch[0],
        'train_data_sample_keys': data_batch[1],
        'traintuple_id': uuid.uuid4().hex,
        'in_models_ids': [previous_id] if previous_id else [],
    }
    testtuple = {
        'traintuple_id': traintuple['traintuple_id']
    }
    traintuples.append(traintuple)
    testtuples.append(testtuple)
    previous_id = traintuple['traintuple_id']


print('Adding compute plan...')
compute_plan = client.add_compute_plan({
    "algo_key": algo_key,
    "objective_key": objective_key,
    "traintuples": traintuples,
    "testtuples": testtuples,
})
compute_plan_id = compute_plan.get('computePlanID')

with open(compute_plan_keys_path, 'w') as f:
    json.dump(compute_plan, f, indent=2)

print(f'Compute plan keys have been saved to {os.path.abspath(compute_plan_keys_path)}')
