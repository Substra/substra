# substra.sdk

# Client
```python
Client(self, url: Union[str, NoneType] = None, token: Union[str, NoneType] = None, retry_timeout: int = 300, insecure: bool = False, debug: bool = False)
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
Client.from_config_file(profile_name: str = 'default', config_path: Union[str, pathlib.Path] = '~/.substra', tokens_path: Union[str, pathlib.Path] = '~/.substra-tokens', token: Union[str, NoneType] = None, retry_timeout: int = 300, debug: bool = False)
```
Returns a new Client configured with profile data from configuration files.

Args:

    profile_name (str, optional): Name of the profile to load.
        Defaults to 'default'.

    config_path (Union[str, pathlib.Path], optional): Path to the
        configuration file.
        Defaults to '~/.substra'.

    tokens_path (Union[str, pathlib.Path], optional): Path to the tokens file.
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
Client.add_data_sample(self, data: Union[dict, substra.sdk.schemas.DataSampleSpec], local: bool = True, exist_ok: bool = False) -> str
```
Create a new data sample asset and return its key.

If a data sample with the same content already exists, an `AlreadyExists` exception will be
raised.

Args:

    data (Union[dict, schemas.DataSampleSpec]): data sample to add. If it is a dict,
    it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).

    local (bool, optional):
        If `local` is true, `path` must refer to a directory located on the local
        filesystem. The file content will be transferred to the server through an
        HTTP query, so this mode should be used for relatively small files (<10mo).

        If `local` is false, `path` must refer to a directory located on the server
        filesystem. This directory must be accessible (readable) by the server.  This
        mode is well suited for all kind of file sizes. Defaults to True.

    exist_ok (bool, optional):
        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset key will be returned. Defaults to False.

Returns:
    str: key of the data sample

## add_data_samples
```python
Client.add_data_samples(self, data: Union[dict, substra.sdk.schemas.DataSampleSpec], local: bool = True) -> List[str]
```
Create many data sample assets and return  a list of keys.

Create multiple data samples through a single HTTP request.
This method is well suited for adding multiple small files only. For adding a
large amount of data it is recommended to add them one by one. It allows a
better control in case of failures.

If data samples with the same content as any of the paths already exists, an `AlreadyExists`
exception will be raised.

Args:

    data (Union[dict, schemas.DataSampleSpec]): data samples to add. If it is a dict,
        it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).

        The `paths` in the data dictionary must be a list of paths where each path
        points to a directory representing one data sample.

    local (bool, optional):  Please refer to the method `Client.add_data_sample`.
        Defaults to True.

Returns:
    List[str]: List of the data sample keys

## add_dataset
```python
Client.add_dataset(self, data: Union[dict, substra.sdk.schemas.DatasetSpec], exist_ok: bool = False)
```
Create new dataset asset and return its key.

If a dataset with the same opener already exists, an `AlreadyExists` exception will be
raised.

Args:

    data (Union[dict, schemas.DatasetSpec]): If it is a dict, it must have the same
        keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists` exceptions
        will be ignored and the existing asset key will be returned.
        Defaults to False.

Returns:
    str: Key of the dataset

## add_objective
```python
Client.add_objective(self, data: Union[dict, substra.sdk.schemas.ObjectiveSpec], exist_ok: bool = False) -> str
```
Create new objective asset.

If an objective with the same description already exists, an `AlreadyExists` exception will
be raised.

Args:

    data (Union[dict, schemas.ObjectiveSpec]): If it is a dict, it must have the same keys
        as specified in [schemas.ObjectiveSpec](sdk_schemas.md#ObjectiveSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists` exceptions
        will be ignored and the existing asset key will be returned. Defaults to False.

Returns:
    str: Key of the objective

## add_algo
```python
Client.add_algo(self, data: Union[dict, substra.sdk.schemas.AlgoSpec], exist_ok: bool = False) -> str
```
Create new algo asset.

If an algo with the same archive file already exists, an `AlreadyExists` exception will be
raised.

Args:

    data (Union[dict, schemas.AlgoSpec]): If it is a dict, it must have the same keys
        as specified in [schemas.AlgoSpec](sdk_schemas.md#AlgoSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists` exceptions will be
        ignored and the existing asset key will be returned. Defaults to False.

Returns:
    str: Key of the algo

## add_aggregate_algo
```python
Client.add_aggregate_algo(self, data: Union[dict, substra.sdk.schemas.AggregateAlgoSpec], exist_ok: bool = False) -> str
```
Create new aggregate algo asset.

If an aggregate algo with the same archive file already exists, an `AlreadyExists`
exception will be raised.

Args:

    data (Union[dict, schemas.AggregateAlgoSpec]): If it is a dict,
        it must have the same keys as specified in
        [schemas.AggregateAlgoSpec](sdk_schemas.md#AggregateAlgoSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_composite_algo
```python
Client.add_composite_algo(self, data: Union[dict, substra.sdk.schemas.CompositeAlgoSpec], exist_ok: bool = False) -> str
```
Create new composite algo asset.

If a composite algo with the same archive file already exists, an `AlreadyExists`
exception will be raised.

Args:

    data (Union[dict, schemas.CompositeAlgoSpec]): If it is a dict, it must have the same
        keys as specified in [schemas.CompositeAlgoSpec](sdk_schemas.md#CompositeAlgoSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_traintuple
```python
Client.add_traintuple(self, data: Union[dict, substra.sdk.schemas.TraintupleSpec], exist_ok: bool = False) -> str
```
Create new traintuple asset.

An `AlreadyExists` exception will be raised if a traintuple already exists that:
* has the same `algo_key`, `data_manager_key`, `train_data_sample_keys` and `in_models_keys`
* and was created through the same node you are using

Args:

    data (Union[dict, schemas.TraintupleSpec]): If it is a dict, it must have the same
        keys as specified in [schemas.TraintupleSpec](sdk_schemas.md#TraintupleSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_aggregatetuple
```python
Client.add_aggregatetuple(self, data: Union[dict, substra.sdk.schemas.AggregatetupleSpec], exist_ok: bool = False) -> str
```
Create a new aggregate tuple asset.

An `AlreadyExists` exception will be raised if an aggregatetuple already exists that:
* has the same `algo_key` and `in_models_keys`
* and was created through the same node you are using

Args:

    data (Union[dict, schemas.AggregatetupleSpec]): If it is a dict, it must have the same
        keys as specified in
        [schemas.AggregatetupleSpec](sdk_schemas.md#AggregatetupleSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_composite_traintuple
```python
Client.add_composite_traintuple(self, data: Union[dict, substra.sdk.schemas.CompositeTraintupleSpec], exist_ok: bool = False) -> str
```
Create new composite traintuple asset.

As specified in the data structure, output trunk models cannot be made
public.

An `AlreadyExists` exception will be raised if a traintuple already exists that:
* has the same `algo_key`, `data_manager_key`, `train_data_sample_keys`,
  `in_head_models_key` and `in_trunk_model_key`
* and was created through the same node you are using

Args:

    data (Union[dict, schemas.CompositeTraintupleSpec]): If it is a dict, it must have the
        same keys as specified in
        [schemas.CompositeTraintupleSpec](sdk_schemas.md#CompositeTraintupleSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_testtuple
```python
Client.add_testtuple(self, data: Union[dict, substra.sdk.schemas.TesttupleSpec], exist_ok: bool = False) -> str
```
Create new testtuple asset.

An `AlreadyExists` exception will be raised if a testtuple already exists that:
* has the same `traintuple_key`, `objective_key`, `data_manager_key` and
  `test_data_sample_keys`
* and was created through the same node you are using

Args:

    data (Union[dict, schemas.TesttupleSpec]): If it is a dict, it must have the same
        keys as specified in [schemas.TesttupleSpec](sdk_schemas.md#TesttupleSpec).

    exist_ok (bool, optional): If `exist_ok` is true, `AlreadyExists`
        exceptions will be ignored and the existing asset key will be returned.
        Defaults to False.

 Returns:
    str: Key of the asset

## add_compute_plan
```python
Client.add_compute_plan(self, data: Union[dict, substra.sdk.schemas.ComputePlanSpec], auto_batching: bool = True, batch_size: int = 20) -> substra.sdk.models.ComputePlan
```
Create new compute plan asset.

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.

Args:

    data (Union[dict, schemas.ComputePlanSpec]): If it is a dict, it must have the same
        keys as specified in [schemas.ComputePlanSpec](sdk_schemas.md#ComputePlanSpec).

    auto_batching (bool, optional): Set 'auto_batching' to False to upload all the tuples of
        the compute plan at once. Defaults to True.

    batch_size (int, optional): If 'auto_batching' is True, change `batch_size` to define
        the number oftuples uploaded in each batch (default 20).

Returns:
    models.ComputePlan: Created compute plan

## get_algo
```python
Client.get_algo(self, key: str) -> substra.sdk.models.Algo
```
Get algo by key.
## get_compute_plan
```python
Client.get_compute_plan(self, key: str) -> substra.sdk.models.ComputePlan
```
Get compute plan by key.
## get_aggregate_algo
```python
Client.get_aggregate_algo(self, key: str) -> substra.sdk.models.AggregateAlgo
```
Get aggregate algo by key.
## get_composite_algo
```python
Client.get_composite_algo(self, key: str) -> substra.sdk.models.CompositeAlgo
```
Get composite algo by key.
## get_dataset
```python
Client.get_dataset(self, key: str) -> substra.sdk.models.Dataset
```
Get dataset by key.
## get_objective
```python
Client.get_objective(self, key: str) -> substra.sdk.models.Objective
```
Get objective by key.
## get_testtuple
```python
Client.get_testtuple(self, key: str) -> substra.sdk.models.Testtuple
```
Get testtuple by key.
## get_traintuple
```python
Client.get_traintuple(self, key: str) -> substra.sdk.models.Traintuple
```
Get traintuple by key.
## get_aggregatetuple
```python
Client.get_aggregatetuple(self, key: str) -> substra.sdk.models.Aggregatetuple
```
Get aggregatetuple by key.
## get_composite_traintuple
```python
Client.get_composite_traintuple(self, key: str) -> substra.sdk.models.CompositeTraintuple
```
Get composite traintuple by key.
## list_algo
```python
Client.list_algo(self, filters=None) -> List[substra.sdk.models.Algo]
```
List algos.
## list_compute_plan
```python
Client.list_compute_plan(self, filters=None) -> List[substra.sdk.models.ComputePlan]
```
List compute plans.
## list_aggregate_algo
```python
Client.list_aggregate_algo(self, filters=None) -> List[substra.sdk.models.AggregateAlgo]
```
List aggregate algos.
## list_composite_algo
```python
Client.list_composite_algo(self, filters=None) -> List[substra.sdk.models.CompositeAlgo]
```
List composite algos.
## list_data_sample
```python
Client.list_data_sample(self, filters=None) -> List[substra.sdk.models.DataSample]
```
List data samples.
## list_dataset
```python
Client.list_dataset(self, filters=None) -> List[substra.sdk.models.Dataset]
```
List datasets.
## list_objective
```python
Client.list_objective(self, filters=None) -> List[substra.sdk.models.Objective]
```
List objectives.
## list_testtuple
```python
Client.list_testtuple(self, filters=None) -> List[substra.sdk.models.Testtuple]
```
List testtuples.
## list_traintuple
```python
Client.list_traintuple(self, filters=None) -> List[substra.sdk.models.Traintuple]
```
List traintuples.
## list_aggregatetuple
```python
Client.list_aggregatetuple(self, filters=None) -> List[substra.sdk.models.Aggregatetuple]
```
List aggregatetuples.
## list_composite_traintuple
```python
Client.list_composite_traintuple(self, filters=None) -> List[substra.sdk.models.CompositeTraintuple]
```
List composite traintuples.
## list_node
```python
Client.list_node(self, *args, **kwargs) -> List[substra.sdk.models.Node]
```
List nodes.
## update_compute_plan
```python
Client.update_compute_plan(self, compute_plan_id: str, data: Union[dict, substra.sdk.schemas.UpdateComputePlanSpec], auto_batching: bool = True, batch_size: int = 20) -> substra.sdk.models.ComputePlan
```
Update compute plan.

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.

Args:

    compute_plan_id (str): Id of the compute plan

    data (Union[dict, schemas.UpdateComputePlanSpec]): If it is a dict,
        it must have the same keys as specified in
        [schemas.UpdateComputePlanSpec](sdk_schemas.md#UpdateComputePlanSpec).

    auto_batching (bool, optional): Set 'auto_batching' to False to upload all
        the tuples of the compute plan at once. Defaults to True.

    batch_size (int, optional): If 'auto_batching' is True, change `batch_size`
        to define the number of tuples uploaded in each batch (default 20).

Returns:
    models.ComputePlan: updated compute plan

## link_dataset_with_objective
```python
Client.link_dataset_with_objective(self, dataset_key: str, objective_key: str) -> str
```
Link dataset with objective.
## link_dataset_with_data_samples
```python
Client.link_dataset_with_data_samples(self, dataset_key: str, data_sample_keys: str) -> List[str]
```
Link dataset with data samples.
## download_dataset
```python
Client.download_dataset(self, key: str, destination_folder: str) -> None
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, key: str, destination_folder: str) -> None
```
Download algo resource.

Download algo package in destination folder.

## download_aggregate_algo
```python
Client.download_aggregate_algo(self, key: str, destination_folder: str) -> None
```
Download aggregate algo resource.

Download aggregate algo package in destination folder.

## download_composite_algo
```python
Client.download_composite_algo(self, key: str, destination_folder: str) -> None
```
Download composite algo resource.

Download composite algo package in destination folder.

## download_objective
```python
Client.download_objective(self, key: str, destination_folder: str) -> None
```
Download objective resource.

Download metrics script in destination folder.

## describe_algo
```python
Client.describe_algo(self, key: str) -> str
```
Get algo description.
## describe_aggregate_algo
```python
Client.describe_aggregate_algo(self, key: str) -> str
```
Get aggregate algo description.
## describe_composite_algo
```python
Client.describe_composite_algo(self, key: str) -> str
```
Get composite algo description.
## describe_dataset
```python
Client.describe_dataset(self, key: str) -> str
```
Get dataset description.
## describe_objective
```python
Client.describe_objective(self, key: str) -> str
```
Get objective description.
## leaderboard
```python
Client.leaderboard(self, objective_key: str, sort: str = 'desc') -> str
```
Get objective leaderboard
## cancel_compute_plan
```python
Client.cancel_compute_plan(self, compute_plan_id: str) -> substra.sdk.models.ComputePlan
```
Cancel execution of compute plan.
# retry_on_exception
```python
retry_on_exception(exceptions, timeout=300)
```
Retry function in case of exception(s).

Arguments:
    exceptions: list of exception types that trigger a retry
    timeout (int): timeout in seconds

Example:

```python
from substra.sdk import exceptions, retry_on_exception

def my_function(arg1, arg2):
    pass

retry = retry_on_exception(
            exceptions=(exceptions.RequestTimeout),
            timeout=300,
        )
retry(my_function)(arg1, arg2)
```

