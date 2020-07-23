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
current_directory = pathlib.Path(__file__).resolve().parents[1]
assets_directory = current_directory.parent / "titanic" / "assets"
algo_directory = current_directory.parent / "compute_plan" / "assets" / "algo_sgd"

# Define the client
client = substra.Client(debug=True)

DATASET = {
    "name": "Titanic",
    "type": "csv",
    "data_opener": str(assets_directory / "dataset" / "opener.py"),
    "description": str(assets_directory / "dataset" / "description.md"),
    "permissions": {"public": False, "authorized_ids": []},
}

TEST_DATA_SAMPLES_PATHS = [
    assets_directory / "test_data_samples" / path
    for path in (assets_directory / "test_data_samples").glob("*")
]

TRAIN_DATA_SAMPLES_PATHS = [
    assets_directory / "train_data_samples" / path
    for path in (assets_directory / "train_data_samples").glob("*")
]

OBJECTIVE = {
    "name": "Titanic: Machine Learning From Disaster",
    "description": assets_directory / "objective" / "description.md",
    "metrics_name": "accuracy",
    "metrics": assets_directory / "objective" / "metrics.zip",
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
    "file": current_directory / "algo_random_forest.zip",
    "permissions": {"public": False, "authorized_ids": []},
}

ALGO_DOCKERFILE_FILES = [
    assets_directory / "algo_random_forest" / "algo.py",
    assets_directory / "algo_random_forest" / "Dockerfile",
]

with zipfile.ZipFile(ALGO["file"], "w") as z:
    for filepath in ALGO_DOCKERFILE_FILES:
        z.write(filepath, arcname=filepath.name)


# Add the dataset to Substra
print("Adding dataset...")
dataset_key = client.add_dataset(DATASET, exist_ok=True)["pkhash"]
assert dataset_key, "Missing data manager key"

# Add the data samples to Substra
train_data_sample_keys = []
test_data_sample_keys = []
data_samples_configs = (
    {
        "message": "Adding train data samples...",
        "paths": TRAIN_DATA_SAMPLES_PATHS,
        "test_only": False,
        "data_sample_keys": train_data_sample_keys,
        "missing_message": "Missing train data samples keys",
    },
    {
        "message": "Adding test data samples...",
        "paths": TEST_DATA_SAMPLES_PATHS,
        "test_only": True,
        "data_sample_keys": test_data_sample_keys,
        "missing_message": "Missing test data samples keys",
    },
)
for conf in data_samples_configs:
    print(conf["message"])
    with progress_bar(len(conf["paths"])) as progress:
        for path in conf["paths"]:
            data_sample = client.add_data_sample(
                {
                    "data_manager_keys": [dataset_key],
                    "test_only": conf["test_only"],
                    "path": str(path),
                },
                local=True,
                exist_ok=True,
            )
            data_sample_key = data_sample["pkhash"]
            conf["data_sample_keys"].append(data_sample_key)
            progress.update()
    assert len(conf["data_sample_keys"]), conf["missing_message"]

#  Link the dataset to the data samples
#  This is redundant if the 'dataset_key' is in the 'data_manager_keys'
#  of the data samples when they were created.
print("Associating data samples with dataset...")
client.link_dataset_with_data_samples(
    dataset_key, train_data_sample_keys + test_data_sample_keys,
)

#  Add the objective to Substra
print("Adding objective...")
objective_key = client.add_objective(
    {
        "name": OBJECTIVE["name"],
        "description": str(OBJECTIVE["description"]),
        "metrics_name": OBJECTIVE["metrics_name"],
        "metrics": str(OBJECTIVE["metrics"]),
        "test_data_sample_keys": test_data_sample_keys,
        "test_data_manager_key": dataset_key,
        "permissions": OBJECTIVE["permissions"],
    },
    exist_ok=True,
)["pkhash"]
assert objective_key, "Missing objective key"

# Add the algorithm
print("Adding algo...")
algo_key = client.add_algo(
    {
        "name": ALGO["name"],
        "file": str(ALGO["file"]),
        "description": str(ALGO["description"]),
        "permissions": ALGO["permissions"],
    },
    exist_ok=True,
)["pkhash"]

#  Add the traintuple
print("Registering traintuple...")
traintuple = client.add_traintuple(
    {
        "algo_key": algo_key,
        "data_manager_key": dataset_key,
        "train_data_sample_keys": train_data_sample_keys,
    },
    exist_ok=True,
)
traintuple_key = traintuple.get("key") or traintuple.get("pkhash")
assert traintuple_key, "Missing traintuple key"

#  Add the testtuple
print("Registering testtuple...")
testtuple = client.add_testtuple(
    {"objective_key": objective_key, "traintuple_key": traintuple_key}, exist_ok=True
)
testtuple_key = testtuple.get("key") or testtuple.get("pkhash")
assert testtuple_key, "Missing testtuple key"

#  Get the performance
testtuple = client.get_testtuple(key=testtuple_key)
print(f"The performance on the test set is {testtuple['dataset']['perf']:.4f}")
