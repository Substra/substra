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
import pathlib

import substra

# Define the client
client = substra.Client.from_config_file(profile_name="node-1", debug=True)

# Load the keys of the Titanic example assets
assets_keys_path = pathlib.Path(__file__).resolve().parents[2] / "titanic" / "assets_keys.json"
print(f'Loading existing asset keys from {assets_keys_path}...')
with assets_keys_path.open('r') as f:
    assets_keys = json.load(f)

##################
#   Traintuple   #
##################

#  Add the traintuple
print("Registering traintuple...")
traintuple = client.add_traintuple(
    {
        "algo_key": assets_keys["algo_random_forest"]["algo_key"],
        "data_manager_key": assets_keys["dataset_key"],
        "train_data_sample_keys": assets_keys["train_data_sample_keys"],
    },
    exist_ok=True,
)
traintuple_key = traintuple.get("key") or traintuple.get("pkhash")
assert traintuple_key, "Missing traintuple key"

#################
#   Testtuple   #
#################

#  Add the testtuple
print("Registering testtuple...")
testtuple = client.add_testtuple(
    {
        "objective_key": assets_keys["objective_key"],
        "traintuple_key": traintuple_key
    }, exist_ok=True
)
testtuple_key = testtuple.get("key") or testtuple.get("pkhash")
assert testtuple_key, "Missing testtuple key"

###################
#   Performance   #
###################

#  Get the performance
testtuple = client.get_testtuple(key=testtuple_key)
print(f"The performance on the test set is {testtuple['dataset']['perf']:.4f}")
