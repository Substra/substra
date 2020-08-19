# substra.sdk

# Client
```python
Client(self, url:Union[str, NoneType]=None, token:Union[str, NoneType]=None, retry_timeout:int=300, insecure:bool=False, debug:bool=False)
```
Create a client

Args:

    url (str, optional): URL of the Substra platform. Mandatory
        to connect to a Substra platform. If no URL is given debug must be True and all
        assets must be created locally.
        Defaults to None.

    token (str, optional): Token to authenticate to the Substra platform.
        If no token is given, use the 'login' function to authenticate.
        Defaults to None.

    retry_timeout (int, optional): Number of seconds before attempting a retry call in case
        of timeout.
        Defaults to 5 minutes.

    insecure (bool, optional): If True, the client can call a not-certifed backend. This is
        for development purposes.
        Defaults to False.

    debug (bool, optional): Whether to use the default or debug mode.
        In debug mode, new assets are created locally but can access assets from
        the deployed Substra platform. The platform is in read-only mode.
        Defaults to False.

## login
```python
Client.login(self, username, password)
```
Login to a remote server.
## from_config_file
```python
Client.from_config_file(profile_name:str='default', config_path:Union[str, pathlib.Path]='~/.substra', tokens_path:Union[str, pathlib.Path]='~/.substra-tokens', token:Union[str, NoneType]=None, retry_timeout:int=300, debug:bool=False)
```
Returns a new Client configured with profile data from configuration files.

Args:

    profile_name (str, optional): Name of the profile to load.
        Defaults to 'default'.

    config_path (typing.Union[str, pathlib.Path], optional): Path to the
        configuration file.
        Defaults to '~/.substra'.

    tokens_path (typing.Union[str, pathlib.Path], optional): Path to the tokens file.
        Defaults to '~/.substra-tokens'.

    token (str, optional): Token to use for authentication (will be used
        instead of any token found at tokens_path). Defaults to None.

    retry_timeout (int, optional): Number of seconds before attempting a retry call in case
        of timeout. Defaults to 5 minutes.

    debug (bool): Whether to use the default or debug mode. In debug mode, new assets are
        created locally but can get remote assets. The deployed platform is in
        read-only mode.
        Defaults to False.

Returns:
    Client: The new client.

## add_data_sample
```python
Client.add_data_sample(self, data, local=True, exist_ok=False)
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

If a data sample with the same content already exists, an `AlreadyExists` exception will be
raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.


## add_data_samples
```python
Client.add_data_samples(self, data, local=True)
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

If data samples with the same content as any of the paths already exists, an `AlreadyExists`
exception will be raised.

## add_dataset
```python
Client.add_dataset(self, data, exist_ok=False)
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
    "metadata": dict
}
```

If a dataset with the same opener already exists, an `AlreadyExists` exception will be
raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_objective
```python
Client.add_objective(self, data, exist_ok=False)
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
    "metadata": dict
}
```

If an objective with the same description already exists, an `AlreadyExists` exception will
be raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_algo
```python
Client.add_algo(self, data, exist_ok=False)
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
    "metadata": dict
}
```

If an algo with the same archive file already exists, an `AlreadyExists` exception will be
raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_aggregate_algo
```python
Client.add_aggregate_algo(self, data, exist_ok=False)
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
    "metadata": dict
}
```
If an aggregate algo with the same archive file already exists, an `AlreadyExists`
exception will be raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_composite_algo
```python
Client.add_composite_algo(self, data, exist_ok=False)
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
    "metadata": dict
}
```
If a composite algo with the same archive file already exists, an `AlreadyExists` exception
will be raised.

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_traintuple
```python
Client.add_traintuple(self, data, exist_ok=False)
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
    "metadata": dict,
    "rank": int,
    "compute_plan_id": str,
}
```
An `AlreadyExists` exception will be raised if a traintuple already exists that:
* has the same `algo_key`, `data_manager_key`, `train_data_sample_keys` and `in_models_keys`
* and was created through the same node you are using

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_aggregatetuple
```python
Client.add_aggregatetuple(self, data, exist_ok=False)
```
Create new aggregatetuple asset.
`data` is a dict object with the following schema:
```
{
    "algo_key": str,
    "in_models_keys": list[str],
    "tag": str,
    "metadata": dict,
    "compute_plan_id": str,
    "rank": int,
    "worker": str,
}
```
An `AlreadyExists` exception will be raised if an aggregatetuple already exists that:
* has the same `algo_key` and `in_models_keys`
* and was created through the same node you are using

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_composite_traintuple
```python
Client.add_composite_traintuple(self, data, exist_ok=False)
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
    "metadata": dict,
    "rank": int,
    "compute_plan_id": str,
}
```

As specified in the data dict structure, output trunk models cannot be made
public.

An `AlreadyExists` exception will be raised if a traintuple already exists that:
* has the same `algo_key`, `data_manager_key`, `train_data_sample_keys`,
  `in_head_models_key` and `in_trunk_model_key`
* and was created through the same node you are using

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_testtuple
```python
Client.add_testtuple(self, data, exist_ok=False)
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
    "metadata": dict
}
```

An `AlreadyExists` exception will be raised if a testtuple already exists that:
* has the same `traintuple_key`, `objective_key`, `data_manager_key` and
  `test_data_sample_keys`
* and was created through the same node you are using

If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
existing asset will be returned.

## add_compute_plan
```python
Client.add_compute_plan(self, data, auto_batching:bool=True)
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
        "metadata": dict,
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
        "metadata": dict,
    }]
    "aggregatetuples": list[{
        "aggregatetuple_id": str,
        "algo_key": str,
        "worker": str,
        "in_models_ids": list[str],
        "tag": str,
        "metadata": dict,
    }],
    "testtuples": list[{
        "objective_key": str,
        "data_manager_key": str,
        "test_data_sample_keys": list[str],
        "traintuple_id": str,
        "tag": str,
        "metadata": dict,
    }],
    "clean_models": bool,
    "tag": str,
    "metadata": dict
}
```

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.
Set 'auto_batching' to False to upload all the tuples of the
compute plan at once.

## get_algo
```python
Client.get_algo(self, key)
```
Get algo by key.
## get_compute_plan
```python
Client.get_compute_plan(self, key)
```
Get compute plan by key.
## get_aggregate_algo
```python
Client.get_aggregate_algo(self, key)
```
Get aggregate algo by key.
## get_composite_algo
```python
Client.get_composite_algo(self, key)
```
Get composite algo by key.
## get_dataset
```python
Client.get_dataset(self, key)
```
Get dataset by key.
## get_objective
```python
Client.get_objective(self, key)
```
Get objective by key.
## get_testtuple
```python
Client.get_testtuple(self, key)
```
Get testtuple by key.
## get_traintuple
```python
Client.get_traintuple(self, key)
```
Get traintuple by key.
## get_aggregatetuple
```python
Client.get_aggregatetuple(self, key)
```
Get aggregatetuple by key.
## get_composite_traintuple
```python
Client.get_composite_traintuple(self, key)
```
Get composite traintuple by key.
## list_algo
```python
Client.list_algo(self, filters=None)
```
List algos.
## list_compute_plan
```python
Client.list_compute_plan(self, filters=None)
```
List compute plans.
## list_aggregate_algo
```python
Client.list_aggregate_algo(self, filters=None)
```
List aggregate algos.
## list_composite_algo
```python
Client.list_composite_algo(self, filters=None)
```
List composite algos.
## list_data_sample
```python
Client.list_data_sample(self, filters=None)
```
List data samples.
## list_dataset
```python
Client.list_dataset(self, filters=None)
```
List datasets.
## list_objective
```python
Client.list_objective(self, filters=None)
```
List objectives.
## list_testtuple
```python
Client.list_testtuple(self, filters=None)
```
List testtuples.
## list_traintuple
```python
Client.list_traintuple(self, filters=None)
```
List traintuples.
## list_aggregatetuple
```python
Client.list_aggregatetuple(self, filters=None)
```
List aggregatetuples.
## list_composite_traintuple
```python
Client.list_composite_traintuple(self, filters=None)
```
List composite traintuples.
## list_node
```python
Client.list_node(self, *args, **kwargs)
```
List nodes.
## update_compute_plan
```python
Client.update_compute_plan(self, compute_plan_id, data, auto_batching:bool=True)
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
        "metadata": dict,
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
        "metadata": dict,
    }]
    "aggregatetuples": list[{
        "aggregatetuple_id": str,
        "algo_key": str,
        "worker": str,
        "in_models_ids": list[str],
        "tag": str,
        "metadata": dict,
    }],
    "testtuples": list[{
        "objective_key": str,
        "data_manager_key": str,
        "test_data_sample_keys": list[str],
        "traintuple_id": str,
        "tag": str,
        "metadata": dict,
    }]
}
```

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.
Set 'auto_batching' to False to upload all the tuples of the
compute plan at once.

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
Client.download_dataset(self, key, destination_folder)
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, key, destination_folder)
```
Download algo resource.

Download algo package in destination folder.

## download_aggregate_algo
```python
Client.download_aggregate_algo(self, key, destination_folder)
```
Download aggregate algo resource.

Download aggregate algo package in destination folder.

## download_composite_algo
```python
Client.download_composite_algo(self, key, destination_folder)
```
Download composite algo resource.

Download composite algo package in destination folder.

## download_objective
```python
Client.download_objective(self, key, destination_folder)
```
Download objective resource.

Download metrics script in destination folder.

## describe_algo
```python
Client.describe_algo(self, key)
```
Get algo description.
## describe_aggregate_algo
```python
Client.describe_aggregate_algo(self, key)
```
Get aggregate algo description.
## describe_composite_algo
```python
Client.describe_composite_algo(self, key)
```
Get composite algo description.
## describe_dataset
```python
Client.describe_dataset(self, key)
```
Get dataset description.
## describe_objective
```python
Client.describe_objective(self, key)
```
Get objective description.
## leaderboard
```python
Client.leaderboard(self, objective_key, sort='desc')
```
Get objective leaderboard
## cancel_compute_plan
```python
Client.cancel_compute_plan(self, compute_plan_id)
```
Cancel execution of compute plan.
