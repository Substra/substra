# substra.sdk

# Client
```python
Client(self, config_path=None, profile_name=None, user_path=None)
```

## login
```python
Client.login(self)
```
Login.

Allow to login to a remote server.

After setting your configuration with `substra config` using `-u` and `-p`
Launch `substra login`
You will get a token which will be stored by default in `~/.substra-user`
You can change that thanks to the --user option (works like the --profile option)


## set_profile
```python
Client.set_profile(self, profile_name)
```
Set profile from profile name.

If profiles has not been defined through the `add_profile` method, it is loaded
from the config file.

## add_profile
```python
Client.add_profile(self, profile_name, username, password, url, version='0.0', insecure=False)
```
Add new profile (in-memory only).
## add_data_sample
```python
Client.add_data_sample(self, data, local=True, timeout=False, exist_ok=False)
```
Create new data sample asset.

`data` is a dict object with the following schema:

```
{
    "path": str,
    "data_manager_keys": list[str],
    "test_only": bool,
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_data_samples
```python
Client.add_data_samples(self, data, local=True, timeout=False)
```
Create many data sample assets.

`data` is a dict object with the following schema:

```
{
    "paths": list[str],
    "data_manager_keys": list[str],
    "test_only": bool,
}
```

## add_dataset
```python
Client.add_dataset(self, data, timeout=False, exist_ok=False)
```
Create new dataset asset.

`data` is a dict object with the following schema:

```
{
    "name": str,
    "description": str,
    "type": str,
    "data_opener": str,
    "objective_keys": list[str],
    "permissions": {
        "public": bool,
        "authorized_ids": list[str],
    },
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_objective
```python
Client.add_objective(self, data, timeout=False, exist_ok=False)
```
Create new objective asset.

`data` is a dict object with the following schema:

```
{
    "name": str,
    "description": str,
    "metrics_name": str,
    "metrics": str,
    "test_data_manager_key": str,
    "test_data_sample_keys": list[str],
    "permissions": {
        "public": bool,
        "authorized_ids": list[str],
    },
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_algo
```python
Client.add_algo(self, data, timeout=False, exist_ok=False)
```
Create new algo asset.

`data` is a dict object with the following schema:

```
{
    "name": str,
    "description": str,
    "file": str,
    "permissions": {
        "public": bool,
        "authorized_ids": list[str],
    },
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_traintuple
```python
Client.add_traintuple(self, data, timeout=False, exist_ok=False)
```
Create new traintuple asset.

`data` is a dict object with the following schema:

```
{
    "algo_key": str,
    "objective_key": str,
    "data_manager_key": str,
    "train_data_sample_keys": list[str],
    "in_models_keys": list[str],
    "tag": str,
    "compute_plan_id": str,
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_testtuple
```python
Client.add_testtuple(self, data, timeout=False, exist_ok=False)
```
Create new testtuple asset.

`data` is a dict object with the following schema:

```
{
    "data_manager_key": str,
    "traintuple_key": str,
    "test_data_sample_keys": list[str],
    "tag": str,
    "compute_plan_id": str,
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_compute_plan
```python
Client.add_compute_plan(self, data, timeout=False)
```
Create compute plan.

Data is a dict object with the following schema:

```
{
    "algo_key": str,
    "objective_key": str,
    "traintuples": list[{
        "data_manager_key": str,
        "train_data_sample_keys": list[str],
        "traintuple_id": str,
        "in_models_ids": list[str],
        "tag": str,
    }],
    "testtuples": list[{
        "data_manager_key": str,
        "test_data_sample_keys": list[str],
        "testtuple_id": str,
        "traintuple_id": str,
        "tag": str,
    }]
}
```


## get_algo
```python
Client.get_algo(self, algo_key)
```
Get algo by key.
## get_dataset
```python
Client.get_dataset(self, dataset_key)
```
Get dataset by key.
## get_objective
```python
Client.get_objective(self, objective_key)
```
Get objective by key.
## get_testtuple
```python
Client.get_testtuple(self, testtuple_key)
```
Get testtuple by key.
## get_traintuple
```python
Client.get_traintuple(self, traintuple_key)
```
Get traintuple by key.
## list_algo
```python
Client.list_algo(self, filters=None, is_complex=False)
```
List algos.
## list_data_sample
```python
Client.list_data_sample(self, filters=None, is_complex=False)
```
List data samples.
## list_dataset
```python
Client.list_dataset(self, filters=None, is_complex=False)
```
List datasets.
## list_objective
```python
Client.list_objective(self, filters=None, is_complex=False)
```
List objectives.
## list_testtuple
```python
Client.list_testtuple(self, filters=None, is_complex=False)
```
List testtuples.
## list_traintuple
```python
Client.list_traintuple(self, filters=None, is_complex=False)
```
List traintuples.
## list_node
```python
Client.list_node(self, *args, **kwargs)
```
List nodes.
## update_dataset
```python
Client.update_dataset(self, dataset_key, data)
```
Update dataset.
## link_dataset_with_objective
```python
Client.link_dataset_with_objective(self, dataset_key, objective_key)
```
Link dataset with objective.
## link_dataset_with_data_samples
```python
Client.link_dataset_with_data_samples(self, dataset_key, data_sample_keys)
```
Link dataset with data samples.
## download_dataset
```python
Client.download_dataset(self, asset_key, destination_folder)
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, asset_key, destination_folder)
```
Download algo resource.

Download algo package in destination folder.

## download_objective
```python
Client.download_objective(self, asset_key, destination_folder)
```
Download objective resource.

Download metrics script in destination folder.

## describe_algo
```python
Client.describe_algo(self, asset_key)
```
Get algo description.
## describe_dataset
```python
Client.describe_dataset(self, asset_key)
```
Get dataset description.
## describe_objective
```python
Client.describe_objective(self, asset_key)
```
Get objective description.
## leaderboard
```python
Client.leaderboard(self, objective_key, sort='desc')
```
Get objective leaderboard
