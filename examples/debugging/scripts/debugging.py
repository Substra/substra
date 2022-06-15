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
import zipfile

import substra

# Define the client
client = substra.Client.from_config_file(profile_name="org-1", debug=True)

# Define the current and asset directories
current_directory = pathlib.Path(__file__).resolve().parents[1]
assets_directory = current_directory.parent / "titanic" / "assets"
algo_directory = current_directory.parent / "compute_plan" / "assets" / "algo_sgd"

# Load the keys of the Titanic example assets
assets_keys_path = pathlib.Path(__file__).resolve().parents[2] / "titanic" / "assets_keys.json"
print(f"Loading existing asset keys from {assets_keys_path}...")
with assets_keys_path.open("r") as f:
    assets_keys = json.load(f)

#################
#   Algorithm   #
#################

#  Create the algorithm archive and asset
ALGO = {
    "name": "Titanic: Random Forest",
    "category": "ALGO_SIMPLE",
    "description": assets_directory / "algo_random_forest" / "description.md",
    "file": current_directory / "tmp" / "algo_random_forest.zip",
    "permissions": {"public": False, "authorized_ids": []},
}

ALGO_DOCKERFILE_FILES = [
    assets_directory / "algo_random_forest" / "algo.py",
    assets_directory / "algo_random_forest" / "Dockerfile",
]

with zipfile.ZipFile(ALGO["file"], "w") as z:
    for filepath in ALGO_DOCKERFILE_FILES:
        z.write(filepath, arcname=filepath.name)

# Add the algorithm
print("Adding algo locally...")
algo_key = client.add_algo(
    {
        "name": ALGO["name"],
        "category": ALGO["category"],
        "file": str(ALGO["file"]),
        "description": str(ALGO["description"]),
        "permissions": ALGO["permissions"],
    },
)
print(f"Algo key: {algo_key}")

##################
#   Traintuple   #
##################

# Add the traintuple

# The traintuple depends on the algo created above and the dataset and data samples
# from the Substra platform.
print("Registering traintuple locally, training on fake data...")
print(f"Name of the Docker container: algo-{algo_key}")
traintuple_key = client.add_traintuple(
    {
        "algo_key": algo_key,
        "data_manager_key": assets_keys["dataset_key"],
        "train_data_sample_keys": assets_keys["train_data_sample_keys"],
    },
)
assert traintuple_key, "Missing traintuple key"

traintuple = client.get_traintuple(traintuple_key)

#################
#   Testtuple   #
#################

# Add the testtuple
print("Registering testtuple...")
testtuple_key = client.add_testtuple(
    {
        "metric_keys": [assets_keys["metric_key"]],
        "traintuple_key": traintuple_key,
        "data_manager_key": assets_keys["dataset_key"],
        "test_data_sample_keys": assets_keys["test_data_sample_keys"],
    }
)
assert testtuple_key, "Missing testtuple key"

testtuple = client.get_testtuple(testtuple_key)

###################
#   Performance   #
###################

#  Get the performance
testtuple = client.get_testtuple(key=testtuple_key)
perf = list(testtuple.test.perfs.values())[0]
print(f"The performance on the fake test data is {perf:.4f}")
