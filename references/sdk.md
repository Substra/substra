# substra.sdk

# Client
```python
Client(self, config_path: str = None, profile_name: str = None, user_path: str = None, retry_timeout: int = 300) -> None
```

## login
```python
Client.login(self) -> str
```
Login.

Allow to login to a remote server.

After setting your configuration with `substra config` using `-u` and `-p`
Launch `substra login`
You will get a token which will be stored by default in `~/.substra-user`
You can change that thanks to the --user option (works like the --profile option)


## set_profile
```python
Client.set_profile(self, profile_name: str) -> Dict[str, str]
```
Set profile from profile name.

If profiles has not been defined through the `add_profile` method, it is loaded
from the config file.

## add_profile
```python
Client.add_profile(self, profile_name: str, username: str, password: str, url: str, version: str = '0.0', insecure: bool = False) -> Dict[str, str]
```
Add new profile (in-memory only).
## add_data_sample
```python
Client.add_data_sample(self, data: dict, local: bool = True, exist_ok: bool = False) -> dict
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
The `path` in the data dictionary must point to a directory representing the
data sample content. Note that the directory can contain multiple files, all the
directory content will be added to the platform.

If `local` is true, `path` must refer to a directory located on the local
filesystem. The file content will be transferred to the server through an
HTTP query, so this mode should be used for relatively small files (<10mo).

If `local` is false, `path` must refer to a directory located on the server
filesystem. This directory must be accessible (readable) by the server.  This
mode is well suited for all kind of file sizes.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.


## add_data_samples
```python
Client.add_data_samples(self, data: dict, local: bool = True) -> List[dict]
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
Create multiple data samples through a single HTTP request.

The `paths` in the data dictionary must be a list of paths where each path
points to a directory representing one data sample.

For the `local` argument, please refer to the method `Client.add_data_sample`.

This method is well suited for adding multiple small files only. For adding a
large amount of data it is recommended to add them one by one. It allows a
better control in case of failures.

## add_dataset
```python
Client.add_dataset(self, data: dict, exist_ok: bool = False) -> dict
```
Create new dataset asset.

`data` is a dict object with the following schema:

```
{
    "name": str,
    "description": str,
    "type": str,
    "data_opener": str,
    "objective_key": str,
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
Client.add_objective(self, data: dict, exist_ok: bool = False) -> dict
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
Client.add_algo(self, data: dict, exist_ok: bool = False) -> dict
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

## add_aggregate_algo
```python
Client.add_aggregate_algo(self, data: dict, exist_ok: bool = False) -> dict
```
Create new aggregate algo asset.
`data` is a dict object with the following schema:
```
{
    "name": str,
    "description": str,
    "file": str,
    "permissions": {
        "public": bool,
        "authorizedIDs": list[str],
    },
}
```
If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_composite_algo
```python
Client.add_composite_algo(self, data: dict, exist_ok: bool = False) -> dict
```
Create new composite algo asset.
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
Client.add_traintuple(self, data: dict, exist_ok: bool = False) -> dict
```
Create new traintuple asset.

`data` is a dict object with the following schema:

```
{
    "algo_key": str,
    "data_manager_key": str,
    "train_data_sample_keys": list[str],
    "in_models_keys": list[str],
    "tag": str,
    "rank": int,
    "compute_plan_id": str,
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_aggregatetuple
```python
Client.add_aggregatetuple(self, data: dict, exist_ok: bool = False) -> dict
```
Create new aggregatetuple asset.
`data` is a dict object with the following schema:
```
{
    "algo_key": str,
    "in_models_keys": list[str],
    "tag": str,
    "compute_plan_id": str,
    "rank": int,
    "worker": str,
}
```
If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_composite_traintuple
```python
Client.add_composite_traintuple(self, data: dict, exist_ok: bool = False) -> dict
```
Create new composite traintuple asset.
`data` is a dict object with the following schema:
```
{
    "algo_key": str,
    "data_manager_key": str,
    "in_head_model_key": str,
    "in_trunk_model_key": str,
    "out_trunk_model_permissions": {
        "authorized_ids": list[str],
    },
    "tag": str,
    "rank": int,
    "compute_plan_id": str,
}
```

As specified in the data dict structure, output trunk models cannot be made
public.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_testtuple
```python
Client.add_testtuple(self, data: dict, exist_ok: bool = False) -> dict
```
Create new testtuple asset.

`data` is a dict object with the following schema:

```
{
    "objective_key": str,
    "data_manager_key": str,
    "traintuple_key": str,
    "test_data_sample_keys": list[str],
    "tag": str,
}
```

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_compute_plan
```python
Client.add_compute_plan(self, data: dict) -> dict
```
Create compute plan.

Data is a dict object with the following schema:

```
{
    "traintuples": list[{
        "traintuple_id": str,
        "algo_key": str,
        "data_manager_key": str,
        "train_data_sample_keys": list[str],
        "in_models_ids": list[str],
        "tag": str,
    }],
    "composite_traintuples": list[{
        "composite_traintuple_id": str,
        "algo_key": str,
        "data_manager_key": str,
        "train_data_sample_keys": list[str],
        "in_head_model_id": str,
        "in_trunk_model_id": str,
        "out_trunk_model_permissions": {
            "authorized_ids": list[str],
        },
        "tag": str,
    }]
    "aggregatetuples": list[{
        "aggregatetuple_id": str,
        "algo_key": str,
        "worker": str,
        "in_models_ids": list[str],
        "tag": str,
    }],
    "testtuples": list[{
        "objective_key": str,
        "data_manager_key": str,
        "test_data_sample_keys": list[str],
        "traintuple_id": str,
        "tag": str,
    }]
}
```

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.

## get_algo
```python
Client.get_algo(self, algo_key: str) -> dict
```
Get algo by key.
## get_compute_plan
```python
Client.get_compute_plan(self, compute_plan_key: str) -> dict
```
Get compute plan by key.
## get_aggregate_algo
```python
Client.get_aggregate_algo(self, aggregate_algo_key: str) -> dict
```
Get aggregate algo by key.
## get_composite_algo
```python
Client.get_composite_algo(self, composite_algo_key: str) -> dict
```
Get composite algo by key.
## get_dataset
```python
Client.get_dataset(self, dataset_key: str) -> dict
```
Get dataset by key.
## get_objective
```python
Client.get_objective(self, objective_key: str) -> dict
```
Get objective by key.
## get_testtuple
```python
Client.get_testtuple(self, testtuple_key: str) -> dict
```
Get testtuple by key.
## get_traintuple
```python
Client.get_traintuple(self, traintuple_key: str) -> dict
```
Get traintuple by key.
## get_aggregatetuple
```python
Client.get_aggregatetuple(self, aggregatetuple_key: str) -> dict
```
Get aggregatetuple by key.
## get_composite_traintuple
```python
Client.get_composite_traintuple(self, composite_traintuple_key: str) -> dict
```
Get composite traintuple by key.
## list_algo
```python
Client.list_algo(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List algos.
## list_compute_plan
```python
Client.list_compute_plan(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List compute plans.
## list_aggregate_algo
```python
Client.list_aggregate_algo(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List aggregate algos.
## list_composite_algo
```python
Client.list_composite_algo(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List composite algos.
## list_data_sample
```python
Client.list_data_sample(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List data samples.
## list_dataset
```python
Client.list_dataset(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List datasets.
## list_objective
```python
Client.list_objective(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List objectives.
## list_testtuple
```python
Client.list_testtuple(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List testtuples.
## list_traintuple
```python
Client.list_traintuple(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List traintuples.
## list_aggregatetuple
```python
Client.list_aggregatetuple(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List aggregatetuples.
## list_composite_traintuple
```python
Client.list_composite_traintuple(self, filters: Union[List[str], NoneType] = None, is_complex: bool = False) -> List[dict]
```
List composite traintuples.
## list_node
```python
Client.list_node(self) -> List[dict]
```
List nodes.
## update_dataset
```python
Client.update_dataset(self, dataset_key: str, data: dict) -> dict
```
Update dataset.
## update_compute_plan
```python
Client.update_compute_plan(self, compute_plan_id: str, data: dict) -> dict
```
Update compute plan.

Data is a dict object with the following schema:

```
{
    "traintuples": list[{
        "traintuple_id": str,
        "algo_key": str,
        "data_manager_key": str,
        "train_data_sample_keys": list[str],
        "in_models_ids": list[str],
        "tag": str,
    }],
    "composite_traintuples": list[{
        "composite_traintuple_id": str,
        "algo_key": str,
        "data_manager_key": str,
        "train_data_sample_keys": list[str],
        "in_head_model_id": str,
        "in_trunk_model_id": str,
        "out_trunk_model_permissions": {
            "authorized_ids": list[str],
        },
        "tag": str,
    }]
    "aggregatetuples": list[{
        "aggregatetuple_id": str,
        "algo_key": str,
        "worker": str,
        "in_models_ids": list[str],
        "tag": str,
    }],
    "testtuples": list[{
        "objective_key": str,
        "data_manager_key": str,
        "test_data_sample_keys": list[str],
        "traintuple_id": str,
        "tag": str,
    }]
}
```

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.


## link_dataset_with_objective
```python
Client.link_dataset_with_objective(self, dataset_key: str, objective_key: str) -> dict
```
Link dataset with objective.
## link_dataset_with_data_samples
```python
Client.link_dataset_with_data_samples(self, dataset_key: str, data_sample_keys: List[str]) -> dict
```
Link dataset with data samples.
## download_dataset
```python
Client.download_dataset(self, asset_key: str, destination_folder: str) -> None
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, asset_key: str, destination_folder: str) -> None
```
Download algo resource.

Download algo package in destination folder.

## download_aggregate_algo
```python
Client.download_aggregate_algo(self, asset_key: str, destination_folder: str) -> None
```
Download aggregate algo resource.

Download aggregate algo package in destination folder.

## download_composite_algo
```python
Client.download_composite_algo(self, asset_key: str, destination_folder: str) -> None
```
Download composite algo resource.

Download composite algo package in destination folder.

## download_objective
```python
Client.download_objective(self, asset_key: str, destination_folder: str) -> None
```
Download objective resource.

Download metrics script in destination folder.

## describe_algo
```python
Client.describe_algo(self, asset_key: str) -> str
```
Get algo description.
## describe_aggregate_algo
```python
Client.describe_aggregate_algo(self, asset_key: str) -> str
```
Get aggregate algo description.
## describe_composite_algo
```python
Client.describe_composite_algo(self, asset_key: str) -> str
```
Get composite algo description.
## describe_dataset
```python
Client.describe_dataset(self, asset_key: str) -> str
```
Get dataset description.
## describe_objective
```python
Client.describe_objective(self, asset_key: str) -> str
```
Get objective description.
## leaderboard
```python
Client.leaderboard(self, objective_key: str, sort: str = 'desc') -> dict
```
Get objective leaderboard
## cancel_compute_plan
```python
Client.cancel_compute_plan(self, compute_plan_id: str) -> dict
```
Cancel execution of compute plan.
