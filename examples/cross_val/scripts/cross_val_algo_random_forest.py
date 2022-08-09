import hashlib
import json
import os

import substra

current_directory = os.path.dirname(__file__)
assets_keys_path = os.path.join(current_directory, "../../titanic/assets_keys.json")
folds_keys_path = os.path.join(current_directory, "../folds_keys.json")

client = substra.Client.from_config_file(profile_name="organization-1")

print(f"Loading existing asset keys from {os.path.abspath(assets_keys_path)}...")
with open(assets_keys_path, "r") as f:
    assets_keys = json.load(f)

algo_key = assets_keys["algo_random_forest"]["algo_key"]
metric_key = assets_keys["metric_key"]
dataset_key = assets_keys["dataset_key"]

print(f"Loading folds keys from {os.path.abspath(folds_keys_path)}...")
with open(folds_keys_path, "r") as f:
    folds_keys = json.load(f)

tag = hashlib.sha256(str(folds_keys).encode()).hexdigest()
folds_keys["tag"] = tag

for i, fold in enumerate(folds_keys["folds"]):
    print(f"Adding train and test tuples for fold #{i+1}...")
    # traintuple
    traintuple_key = client.add_traintuple(
        {
            "algo_key": algo_key,
            "data_manager_key": dataset_key,
            "train_data_sample_keys": fold["train_data_sample_keys"],
            "tag": tag,
        }
    )
    fold["traintuple_key"] = traintuple_key

    # testtuple
    testtuple_key = client.add_testtuple(
        {
            "metric_keys": [metric_key],
            "traintuple_key": traintuple_key,
            "data_manager_key": dataset_key,
            "test_data_sample_keys": fold["test_data_sample_keys"],
            "tag": tag,
        }
    )
    fold["testtuple_key"] = testtuple_key

with open(folds_keys_path, "w") as f:
    json.dump(folds_keys, f, indent=2)

print(f"Tuples keys have been saved to {os.path.abspath(folds_keys_path)}")
