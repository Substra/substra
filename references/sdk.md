# substra.sdk

# Client
```python
Client(url: Union[str, NoneType] = None, token: Union[str, NoneType] = None, retry_timeout: int = 300, insecure: bool = False, debug: bool = False)
```

Create a client

**Arguments:**
 - `url (str, optional)`: URL of the Substra platform. Mandatory
to connect to a Substra platform. If no URL is given debug must be True and all
assets must be created locally.
Defaults to None.
 - `token (str, optional)`: Token to authenticate to the Substra platform.
If no token is given, use the 'login' function to authenticate.
Defaults to None.
 - `retry_timeout (int, optional)`: Number of seconds before attempting a retry call in case
of timeout.
Defaults to 5 minutes.
 - `insecure (bool, optional)`: If True, the client can call a not-certified backend. This is
for development purposes.
Defaults to False.
 - `debug (bool, optional)`: Whether to use the default or debug mode.
In debug mode, new assets are created locally but can access assets from
the deployed Substra platform. The platform is in read-only mode.
Defaults to False.
## temp_directory
_This is a property._  
Temporary directory for storing assets in debug mode.
        Deleted when the client is deleted.
        
## add_aggregate_algo
```python
add_aggregate_algo(self, data: Union[dict, substra.sdk.schemas.AggregateAlgoSpec]) -> str
```

Create new aggregate algo asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the aggregate algo.

**Arguments:**
 - `data (Union[dict, schemas.AggregateAlgoSpec], required)`: If it is a dict,
it must have the same keys as specified in
[schemas.AggregateAlgoSpec](sdk_schemas.md#AggregateAlgoSpec).

**Returns:**

 - `str`: Key of the asset
## add_aggregatetuple
```python
add_aggregatetuple(self, data: Union[dict, substra.sdk.schemas.AggregatetupleSpec]) -> str
```

Create a new aggregate tuple asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the aggregate tuple.

**Arguments:**
 - `data (Union[dict, schemas.AggregatetupleSpec], required)`: If it is a dict, it must have the same
keys as specified in
[schemas.AggregatetupleSpec](sdk_schemas.md#AggregatetupleSpec).

**Returns:**

 - `str`: Key of the asset
## add_algo
```python
add_algo(self, data: Union[dict, substra.sdk.schemas.AlgoSpec]) -> str
```

Create new algo asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the algo.

**Arguments:**
 - `data (Union[dict, schemas.AlgoSpec], required)`: If it is a dict, it must have the same keys
as specified in [schemas.AlgoSpec](sdk_schemas.md#AlgoSpec).

**Returns:**

 - `str`: Key of the algo
## add_composite_algo
```python
add_composite_algo(self, data: Union[dict, substra.sdk.schemas.CompositeAlgoSpec]) -> str
```

Create new composite algo asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the composite algo.

**Arguments:**
 - `data (Union[dict, schemas.CompositeAlgoSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.CompositeAlgoSpec](sdk_schemas.md#CompositeAlgoSpec).

**Returns:**

 - `str`: Key of the asset
## add_composite_traintuple
```python
add_composite_traintuple(self, data: Union[dict, substra.sdk.schemas.CompositeTraintupleSpec]) -> str
```

Create new composite traintuple asset.
As specified in the data structure, output trunk models cannot be made
public.

In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the composite traintuple.

**Arguments:**
 - `data (Union[dict, schemas.CompositeTraintupleSpec], required)`: If it is a dict, it must have the
same keys as specified in
[schemas.CompositeTraintupleSpec](sdk_schemas.md#CompositeTraintupleSpec).

**Returns:**

 - `str`: Key of the asset
## add_compute_plan
```python
add_compute_plan(self, data: Union[dict, substra.sdk.schemas.ComputePlanSpec], auto_batching: bool = True, batch_size: int = 20) -> substra.sdk.models.ComputePlan
```

Create new compute plan asset.
As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.

**Arguments:**
 - `data (Union[dict, schemas.ComputePlanSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.ComputePlanSpec](sdk_schemas.md#ComputePlanSpec).
 - `auto_batching (bool, optional)`: Set 'auto_batching' to False to upload all the tuples of
the compute plan at once. Defaults to True.
 - `batch_size (int, optional)`: If 'auto_batching' is True, change `batch_size` to define
the number of tuples uploaded in each batch (default 20).

**Returns:**

 - `models.ComputePlan`: Created compute plan
## add_data_sample
```python
add_data_sample(self, data: Union[dict, substra.sdk.schemas.DataSampleSpec], local: bool = True) -> str
```

Create a new data sample asset and return its key.

**Arguments:**
 - `data (Union[dict, schemas.DataSampleSpec], required)`: data sample to add. If it is a dict,
it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).
 - `local (bool, optional)`: If `local` is true, `path` must refer to a directory located
on the local filesystem. The file content will be transferred to the server
through an HTTP query, so this mode should be used for relatively small files
(<10mo).

If `local` is false, `path` must refer to a directory located on the server
filesystem. This directory must be accessible (readable) by the server.  This
mode is well suited for all kind of file sizes. Defaults to True.

**Returns:**

 - `str`: key of the data sample
## add_data_samples
```python
add_data_samples(self, data: Union[dict, substra.sdk.schemas.DataSampleSpec], local: bool = True) -> List[str]
```

Create many data sample assets and return  a list of keys.
Create multiple data samples through a single HTTP request.
This method is well suited for adding multiple small files only. For adding a
large amount of data it is recommended to add them one by one. It allows a
better control in case of failures.

**Arguments:**
 - `data (Union[dict, schemas.DataSampleSpec], required)`: data samples to add. If it is a dict,
it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).
The `paths` in the data dictionary must be a list of paths where each path
points to a directory representing one data sample.
 - `local (bool, optional)`:  Please refer to the method `Client.add_data_sample`.
Defaults to True.

**Returns:**

 - `List[str]`: List of the data sample keys
## add_dataset
```python
add_dataset(self, data: Union[dict, substra.sdk.schemas.DatasetSpec])
```

Create new dataset asset and return its key.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the node owner of the data, and all tuples using this data
have their worker set to this node. This has no impact on how the tuples are
executed except if chainkey support is enabled.

**Arguments:**
 - `data (Union[dict, schemas.DatasetSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

**Returns:**

 - `str`: Key of the dataset
## add_objective
```python
add_objective(self, data: Union[dict, substra.sdk.schemas.ObjectiveSpec]) -> str
```

Create new objective asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the objective.

**Arguments:**
 - `data (Union[dict, schemas.ObjectiveSpec], required)`: If it is a dict, it must have the same keys
as specified in [schemas.ObjectiveSpec](sdk_schemas.md#ObjectiveSpec).

**Returns:**

 - `str`: Key of the objective
## add_testtuple
```python
add_testtuple(self, data: Union[dict, substra.sdk.schemas.TesttupleSpec]) -> str
```

Create new testtuple asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the testtuple.

**Arguments:**
 - `data (Union[dict, schemas.TesttupleSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.TesttupleSpec](sdk_schemas.md#TesttupleSpec).

**Returns:**

 - `str`: Key of the asset
## add_traintuple
```python
add_traintuple(self, data: Union[dict, substra.sdk.schemas.TraintupleSpec]) -> str
```

Create new traintuple asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the traintuple.

**Arguments:**
 - `data (Union[dict, schemas.TraintupleSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.TraintupleSpec](sdk_schemas.md#TraintupleSpec).

**Returns:**

 - `str`: Key of the asset
## cancel_compute_plan
```python
cancel_compute_plan(self, key: str) -> substra.sdk.models.ComputePlan
```

Cancel execution of compute plan, the returned object is described
in the [models.ComputePlan](sdk_models.md#ComputePlan) model
## describe_aggregate_algo
```python
describe_aggregate_algo(self, key: str) -> str
```

Get aggregate algo description.
## describe_algo
```python
describe_algo(self, key: str) -> str
```

Get algo description.
## describe_composite_algo
```python
describe_composite_algo(self, key: str) -> str
```

Get composite algo description.
## describe_dataset
```python
describe_dataset(self, key: str) -> str
```

Get dataset description.
## describe_objective
```python
describe_objective(self, key: str) -> str
```

Get objective description.
## download_aggregate_algo
```python
download_aggregate_algo(self, key: str, destination_folder: str) -> None
```

Download aggregate algo resource.
Download aggregate algo package in destination folder.
## download_algo
```python
download_algo(self, key: str, destination_folder: str) -> None
```

Download algo resource.
Download algo package in destination folder.
## download_composite_algo
```python
download_composite_algo(self, key: str, destination_folder: str) -> None
```

Download composite algo resource.
Download composite algo package in destination folder.
## download_dataset
```python
download_dataset(self, key: str, destination_folder: str) -> None
```

Download data manager resource.
Download opener script in destination folder.
## download_head_model_from_composite_traintuple
```python
download_head_model_from_composite_traintuple(self, tuple_key: str, folder) -> None
```

Download composite traintuple head model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_model
```python
download_model(self, key: str, folder) -> None
```

Download model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_model_from_aggregatetuple
```python
download_model_from_aggregatetuple(self, tuple_key: str, folder) -> None
```

Download aggregatetuple model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_model_from_traintuple
```python
download_model_from_traintuple(self, tuple_key: str, folder) -> None
```

Download traintuple model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_objective
```python
download_objective(self, key: str, destination_folder: str) -> None
```

Download objective resource.
Download metrics script in destination folder.
## download_trunk_model_from_composite_traintuple
```python
download_trunk_model_from_composite_traintuple(self, tuple_key: str, folder) -> None
```

Download composite traintuple trunk model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## from_config_file
```python
from_config_file(profile_name: str = 'default', config_path: Union[str, pathlib.Path] = '~/.substra', tokens_path: Union[str, pathlib.Path] = '~/.substra-tokens', token: Union[str, NoneType] = None, retry_timeout: int = 300, debug: bool = False)
```

Returns a new Client configured with profile data from configuration files.

**Arguments:**
 - `profile_name (str, optional)`: Name of the profile to load.
Defaults to 'default'.
 - `config_path (Union[str, pathlib.Path], optional)`: Path to the
configuration file.
Defaults to '~/.substra'.
 - `tokens_path (Union[str, pathlib.Path], optional)`: Path to the tokens file.
Defaults to '~/.substra-tokens'.
 - `token (str, optional)`: Token to use for authentication (will be used
instead of any token found at tokens_path). Defaults to None.
 - `retry_timeout (int, optional)`: Number of seconds before attempting a retry call in case
of timeout. Defaults to 5 minutes.
 - `debug (bool, required)`: Whether to use the default or debug mode. In debug mode, new assets are
created locally but can get remote assets. The deployed platform is in
read-only mode.
Defaults to False.

**Returns:**

 - `Client`: The new client.
## get_aggregate_algo
```python
get_aggregate_algo(self, key: str) -> substra.sdk.models.AggregateAlgo
```

Get aggregate algo by key, the returned object is described
in the [models.AggregateAlgo](sdk_models.md#AggregateAlgo) model
## get_aggregatetuple
```python
get_aggregatetuple(self, key: str) -> substra.sdk.models.Aggregatetuple
```

Get aggregatetuple by key, the returned object is described
in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model
## get_algo
```python
get_algo(self, key: str) -> substra.sdk.models.Algo
```

Get algo by key, the returned object is described
in the [models.Algo](sdk_models.md#Algo) model
## get_composite_algo
```python
get_composite_algo(self, key: str) -> substra.sdk.models.CompositeAlgo
```

Get composite algo by key, the returned object is described
in the [models.CompositeAlgo](sdk_models.md#CompositeAlgo) model
## get_composite_traintuple
```python
get_composite_traintuple(self, key: str) -> substra.sdk.models.CompositeTraintuple
```

Get composite traintuple by key, the returned object is described
in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model
## get_compute_plan
```python
get_compute_plan(self, key: str) -> substra.sdk.models.ComputePlan
```

Get compute plan by key, the returned object is described
in the [models.ComputePlan](sdk_models.md#ComputePlan) model
## get_dataset
```python
get_dataset(self, key: str) -> substra.sdk.models.Dataset
```

Get dataset by key, the returned object is described
in the [models.Dataset](sdk_models.md#Dataset) model
## get_objective
```python
get_objective(self, key: str) -> substra.sdk.models.Objective
```

Get objective by key, the returned object is described
in the [models.Objective](sdk_models.md#Objective) model
## get_testtuple
```python
get_testtuple(self, key: str) -> substra.sdk.models.Testtuple
```

Get testtuple by key, the returned object is described
in the [models.Testtuple](sdk_models.md#Testtuple) model
## get_traintuple
```python
get_traintuple(self, key: str) -> substra.sdk.models.Traintuple
```

Get traintuple by key, the returned object is described
in the [models.Traintuple](sdk_models.md#Traintuple) model
## leaderboard
```python
leaderboard(self, objective_key: str, sort: str = 'desc') -> str
```

Get objective leaderboard
## link_dataset_with_data_samples
```python
link_dataset_with_data_samples(self, dataset_key: str, data_sample_keys: str) -> List[str]
```

Link dataset with data samples.
## link_dataset_with_objective
```python
link_dataset_with_objective(self, dataset_key: str, objective_key: str) -> str
```

Link dataset with objective.
## list_aggregate_algo
```python
list_aggregate_algo(self, filters=None) -> List[substra.sdk.models.AggregateAlgo]
```

List aggregate algos, the returned object is described
in the [models.AggregateAlgo](sdk_models.md#AggregateAlgo) model
## list_aggregatetuple
```python
list_aggregatetuple(self, filters=None) -> List[substra.sdk.models.Aggregatetuple]
```

List aggregatetuples, the returned object is described
in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model
## list_algo
```python
list_algo(self, filters=None) -> List[substra.sdk.models.Algo]
```

List algos, the returned object is described
in the [models.Algo](sdk_models.md#Algo) model
## list_composite_algo
```python
list_composite_algo(self, filters=None) -> List[substra.sdk.models.CompositeAlgo]
```

List composite algos, the returned object is described
in the [models.CompositeAlgo](sdk_models.md#CompositeAlgo) model
## list_composite_traintuple
```python
list_composite_traintuple(self, filters=None) -> List[substra.sdk.models.CompositeTraintuple]
```

List composite traintuples, the returned object is described
in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model
## list_compute_plan
```python
list_compute_plan(self, filters=None) -> List[substra.sdk.models.ComputePlan]
```

List compute plans, the returned object is described
in the [models.ComputePlan](sdk_models.md#ComputePlan) model
## list_data_sample
```python
list_data_sample(self, filters=None) -> List[substra.sdk.models.DataSample]
```

List data samples, the returned object is described
in the [models.DataSample](sdk_models.md#DataSample) model
## list_dataset
```python
list_dataset(self, filters=None) -> List[substra.sdk.models.Dataset]
```

List datasets, the returned object is described
in the [models.Dataset](sdk_models.md#Dataset) model
## list_node
```python
list_node(self, *args, **kwargs) -> List[substra.sdk.models.Node]
```

List nodes, the returned object is described
in the [models.Node](sdk_models.md#Node) model
## list_objective
```python
list_objective(self, filters=None) -> List[substra.sdk.models.Objective]
```

List objectives, the returned object is described
in the [models.Objective](sdk_models.md#Objective) model
## list_testtuple
```python
list_testtuple(self, filters=None) -> List[substra.sdk.models.Testtuple]
```

List testtuples, the returned object is described
in the [models.Testtuple](sdk_models.md#Testtuple) model
## list_traintuple
```python
list_traintuple(self, filters=None) -> List[substra.sdk.models.Traintuple]
```

List traintuples, the returned object is described
in the [models.Traintuple](sdk_models.md#Traintuple) model
## login
```python
login(self, username, password)
```

Login to a remote server. 
## node_info
```python
node_info(self) -> str
```

Get node information.
## update_compute_plan
```python
update_compute_plan(self, key: str, data: Union[dict, substra.sdk.schemas.UpdateComputePlanSpec], auto_batching: bool = True, batch_size: int = 20) -> substra.sdk.models.ComputePlan
```

Update compute plan.
As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.

**Arguments:**
 - `key (str, required)`: Compute plan key
 - `data (Union[dict, schemas.UpdateComputePlanSpec], required)`: If it is a dict,
it must have the same keys as specified in
[schemas.UpdateComputePlanSpec](sdk_schemas.md#UpdateComputePlanSpec).
 - `auto_batching (bool, optional)`: Set 'auto_batching' to False to upload all
the tuples of the compute plan at once. Defaults to True.
 - `batch_size (int, optional)`: If 'auto_batching' is True, change `batch_size`
to define the number of tuples uploaded in each batch (default 20).

**Returns:**

 - `models.ComputePlan`: updated compute plan, as described in the
[models.ComputePlan](sdk_models.md#ComputePlan) model
# retry_on_exception
```python
retry_on_exception(exceptions, timeout=300)
```

Retry function in case of exception(s).

**Arguments:**
 - `exceptions (list, required)`: list of exception types that trigger a retry
 - `timeout (int, optional)`: timeout in seconds

**Examples:**
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
