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
import logging
import pathlib
import zipfile
from contextlib import contextmanager
from types import SimpleNamespace

from tqdm import tqdm

import substra

default_stream_handler = logging.StreamHandler()
substra_logger = logging.getLogger("substra")
substra_logger.addHandler(default_stream_handler)


@contextmanager
def progress_bar(length):
    """Provide progress bar for for loops"""
    pg = tqdm(total=length)
    progress_handler = logging.StreamHandler(
        SimpleNamespace(write=lambda x: pg.write(x, end=""))
    )
    substra_logger.removeHandler(default_stream_handler)
    substra_logger.addHandler(progress_handler)
    try:
        yield pg
    finally:
        pg.close()
        substra_logger.removeHandler(progress_handler)
        substra_logger.addHandler(default_stream_handler)


# Define the current and asset directories
tmp_directory = pathlib.Path(__file__).resolve().parents[1] / "tmp"
assets_directory = tmp_directory.parents[1] / "titanic" / "assets"
algo_directory = tmp_directory.parents[1] / "compute_plan" / "assets" / "algo_sgd"

# Download the dataset key from the Titanic example
with (assets_directory.parent / "assets_keys.json").open("r") as f:
    dataset_json = json.load(f)
dataset_key = dataset_json.get("dataset_key")

# Create the remote client
client_remote = substra.Client.from_config_file(profile_name="node-1")

# Create the local client
client_local = substra.Client(backend="local")

########################################################
#         Add the remote dataset to the local client
########################################################

# Download the remote dataset opener
dataset = client_remote.get_dataset(key=dataset_key)
client_remote.download_dataset(
    key=dataset_key, destination_folder=tmp_directory
)

# Download the remote dataset description and save it to a file
dataset_description = client_remote.describe_dataset(key=dataset_key)
dataset_description_path = tmp_directory / "dataset_description.md"
with dataset_description_path.open("w") as f:
    f.write(dataset_description)

# Add the dataset to the local client
local_dataset = client_local.add_dataset(
    data={
        "name": dataset["name"],
        "type": dataset["type"],
        "data_opener": tmp_directory / "opener.py",
        "description": dataset_description_path,
        "permissions": {
            "public": dataset["permissions"]["process"]["public"],
            "authorized_ids": dataset["permissions"]["process"]["authorizedIDs"],
        },
    }
)

########################################################
#         Define the objective and algo
########################################################

OBJECTIVE = {
    "name": "Titanic: Machine Learning From Disaster",
    "description": assets_directory / "objective" / "description.md",
    "metrics_name": "accuracy",
    "metrics": tmp_directory / "metrics.zip",
    "permissions": {"public": False, "authorized_ids": []},
}
METRICS_DOCKERFILE_FILES = [
    assets_directory / "objective" / "metrics.py",
    assets_directory / "objective" / "Dockerfile",
]

archive_path = OBJECTIVE["metrics"]
with zipfile.ZipFile(archive_path, "w") as z:
    for filepath in METRICS_DOCKERFILE_FILES:
        z.write(filepath, arcname=filepath.name)


#  Create the algorithm archive and asset
ALGO = {
    "name": "Titanic: Random Forest",
    "description": assets_directory / "algo_random_forest" / "description.md",
    "file": tmp_directory / "algo_random_forest.zip",
    "permissions": {"public": False, "authorized_ids": []},
}

ALGO_DOCKERFILE_FILES = [
    assets_directory / "algo_random_forest" / "algo.py",
    assets_directory / "algo_random_forest" / "Dockerfile",
]

with zipfile.ZipFile(ALGO["file"], "w") as z:
    for filepath in ALGO_DOCKERFILE_FILES:
        z.write(filepath, arcname=filepath.name)


#  Add the objective to Substra
print("Adding objective...")
objective_key = client_local.add_objective(
    {
        "name": OBJECTIVE["name"],
        "description": str(OBJECTIVE["description"]),
        "metrics_name": OBJECTIVE["metrics_name"],
        "metrics": str(OBJECTIVE["metrics"]),
        "test_data_sample_keys": [],
        "test_data_manager_key": local_dataset["key"],
        "permissions": OBJECTIVE["permissions"],
    },
    exist_ok=True,
)["pkhash"]
assert objective_key, "Missing objective key"

# Add the algorithm
print("Adding algo...")
algo_key = client_local.add_algo(
    {
        "name": ALGO["name"],
        "file": str(ALGO["file"]),
        "description": str(ALGO["description"]),
        "permissions": ALGO["permissions"],
    },
    exist_ok=True,
)["pkhash"]

########################################################
#         Define the traintuple and testtuple
########################################################

#  Add the traintuple
print("Registering traintuple...")
traintuple = client_local.add_traintuple(
    {
        "algo_key": algo_key,
        "data_manager_key": local_dataset["key"],
        "train_data_sample_keys": [],
        "fake_data": True,
        "n_fake_samples": None  # get the default number of samples
    },
    exist_ok=True,
)
traintuple_key = traintuple.get("key") or traintuple.get("pkhash")
assert traintuple_key, "Missing traintuple key"

#  Add the testtuple
print("Registering testtuple...")
testtuple = client_local.add_testtuple(
    {
        "objective_key": objective_key,
        "traintuple_key": traintuple_key,
        "fake_data": True,
        "n_fake_samples": None  # get the default number of samples
    },
    exist_ok=True,
)
testtuple_key = testtuple.get("key") or testtuple.get("pkhash")
assert testtuple_key, "Missing testtuple key"

########################################################
#         Print the performance
########################################################

print(f"The performance on the test set is {testtuple['dataset']['perf']:.4f}")
