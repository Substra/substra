# substra.sdk

# Client
```text
Client(url: Optional[str] = None, token: Optional[str] = None, retry_timeout: int = 300, insecure: bool = False, debug: bool = False)
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
Additionally, you can set the environment variable `DEBUG_SPAWNER` to `docker` if you want the tasks to
be executed in containers (default) or `subprocess` to execute them in Python subprocesses (faster,
experimental: The `Dockerfile` commands are not executed, requires dependencies to be installed locally).
## backend_mode
_This is a property._
Get the backend mode: deployed,
        local and which type of local mode

        Returns:
            str: Backend mode

## temp_directory
_This is a property._
Temporary directory for storing assets in debug mode.
        Deleted when the client is deleted.

## add_aggregatetuple
```text
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
```text
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
## add_composite_traintuple
```text
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
```text
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
```text
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
```text
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
```text
add_dataset(self, data: Union[dict, substra.sdk.schemas.DatasetSpec])
```

Create new dataset asset and return its key.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the organization owner of the data, and all tuples using this data
have their worker set to this organization. This has no impact on how the tuples are
executed except if chainkey support is enabled.

**Arguments:**
 - `data (Union[dict, schemas.DatasetSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

**Returns:**

 - `str`: Key of the dataset
## add_metric
```text
add_metric(self, data: Union[dict, substra.sdk.schemas.MetricSpec]) -> str
```

Create new metric asset.
In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
the value becomes the 'creator' of the metric.

**Arguments:**
 - `data (Union[dict, schemas.MetricSpec], required)`: If it is a dict, it must have the same keys
as specified in [schemas.MetricSpec](sdk_schemas.md#MetricSpec).

**Returns:**

 - `str`: Key of the metric
## add_testtuple
```text
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
```text
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
```text
cancel_compute_plan(self, key: str) -> None
```

Cancel execution of compute plan. Nothing is returned by this method
## describe_algo
```text
describe_algo(self, key: str) -> str
```

Get algo description.
## describe_dataset
```text
describe_dataset(self, key: str) -> str
```

Get dataset description.
## describe_metric
```text
describe_metric(self, key: str) -> str
```

Get metric description.
## download_algo
```text
download_algo(self, key: str, destination_folder: str) -> None
```

Download algo resource.
Download algo package in destination folder.
## download_dataset
```text
download_dataset(self, key: str, destination_folder: str) -> None
```

Download data manager resource.
Download opener script in destination folder.
## download_head_model_from_composite_traintuple
```text
download_head_model_from_composite_traintuple(self, tuple_key: str, folder) -> None
```

Download composite traintuple head model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_logs
```text
download_logs(self, tuple_key: str, folder: str) -> str
```

Download the execution logs of a failed tuple to a destination file.
The logs are saved in the folder to a file named 'tuple_logs_{tuple_key}.txt'.

Logs are only available for tuples that experienced an execution failure.
Attempting to retrieve logs for tuples in any other states or for non-existing
tuples will result in a NotFound error.

**Arguments:**
 - `tuple_key `: the key of the tuple that produced the logs
 - `folder `: the destination directory

**Returns:**
The path of the output file.
## download_metric
```text
download_metric(self, key: str, destination_folder: str) -> None
```

Download metric resource.
Download metrics script in destination folder.
## download_model
```text
download_model(self, key: str, folder) -> None
```

Download model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_model_from_aggregatetuple
```text
download_model_from_aggregatetuple(self, tuple_key: str, folder) -> None
```

Download aggregatetuple model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_model_from_traintuple
```text
download_model_from_traintuple(self, tuple_key: str, folder) -> None
```

Download traintuple model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## download_trunk_model_from_composite_traintuple
```text
download_trunk_model_from_composite_traintuple(self, tuple_key: str, folder) -> None
```

Download composite traintuple trunk model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.
## from_config_file
```text
from_config_file(profile_name: str = 'default', config_path: Union[str, pathlib.Path] = '~/.substra', tokens_path: Union[str, pathlib.Path] = '~/.substra-tokens', token: Optional[str] = None, retry_timeout: int = 300, debug: bool = False)
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
## get_aggregatetuple
```text
get_aggregatetuple(self, key: str) -> substra.sdk.models.Aggregatetuple
```

Get aggregatetuple by key, the returned object is described
in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model
## get_algo
```text
get_algo(self, key: str) -> substra.sdk.models.Algo
```

Get algo by key, the returned object is described
in the [models.Algo](sdk_models.md#Algo) model
## get_composite_traintuple
```text
get_composite_traintuple(self, key: str) -> substra.sdk.models.CompositeTraintuple
```

Get composite traintuple by key, the returned object is described
in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model
## get_compute_plan
```text
get_compute_plan(self, key: str) -> substra.sdk.models.ComputePlan
```

Get compute plan by key, the returned object is described
in the [models.ComputePlan](sdk_models.md#ComputePlan) model
## get_data_sample
```text
get_data_sample(self, key: str) -> substra.sdk.models.DataSample
```

Get data sample by key, the returned object is described
in the [models.Datasample](sdk_models.md#DataSample) model
## get_dataset
```text
get_dataset(self, key: str) -> substra.sdk.models.Dataset
```

Get dataset by key, the returned object is described
in the [models.Dataset](sdk_models.md#Dataset) model
## get_logs
```text
get_logs(self, tuple_key: str) -> str
```

Get tuple logs by tuple key, the returned object is a string
containing the logs.

Logs are only available for tuples that experienced an execution failure.
Attempting to retrieve logs for tuples in any other states or for non-existing
tuples will result in a NotFound error.
## get_metric
```text
get_metric(self, key: str) -> substra.sdk.models.Metric
```

Get metric by key, the returned object is described
in the [models.Metric](sdk_models.md#Metric) model
## get_model
```text
get_model(self, key: str) -> substra.sdk.models.OutModel
```

None
## get_performances
```text
get_performances(self, key: str) -> substra.sdk.models.Performances
```

Get the compute plan performances by key, the returned object is described
in the [models.Performances](sdk_models.md#Performances) and easily convertible
to pandas dataframe.

**Examples:**
```python
perf = client.get_performances(cp_key)
df = pd.DataFrame(perf.dict())
print(df)
```
## get_testtuple
```text
get_testtuple(self, key: str) -> substra.sdk.models.Testtuple
```

Get testtuple by key, the returned object is described
in the [models.Testtuple](sdk_models.md#Testtuple) model
## get_traintuple
```text
get_traintuple(self, key: str) -> substra.sdk.models.Traintuple
```

Get traintuple by key, the returned object is described
in the [models.Traintuple](sdk_models.md#Traintuple) model
## link_dataset_with_data_samples
```text
link_dataset_with_data_samples(self, dataset_key: str, data_sample_keys: str) -> List[str]
```

Link dataset with data samples.
## list_aggregatetuple
```text
list_aggregatetuple(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.Aggregatetuple]
```

List aggregatetuples.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.Aggregatetuple`: the returned object is described
in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model

``Filters allowed keys:``

    key (List[str]): list aggregatetuples with listed keys.

    owner (List[str]): list aggregatetuples with listed owners.

    worker (List[str]): list aggregatetuples which ran on listed workers. Remote only.

    rank (List[int]): list aggregatetuples which are at given ranks.

    status (str): list aggregatetuples with given status.
                    Possible values: 'waiting', 'todo', 'doing', 'done', 'canceled', 'failed'

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list aggregatetuples matching provided conditions in metadata. Remote only.
    compute_plan_key (str): list aggregatetuples that are in the given compute plan. Remote only.
    algo_key (str): list aggregatetuples that used the given algo. Remote only.
    dataset_key (str): list aggregatetuples linked or using this dataset. Remote only.
    data_sample_key (List[str]): list aggregatetuples linked or that used this data sample(s). Remote only.
## list_algo
```text
list_algo(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.Algo]
```

List algos.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**

 - `models.Algo`: the returned object is described in the [models.Algo](sdk_models.md#Algo) model
``Filters allowed keys:``

    key (List[str]): list algo with given keys.

    name (str): list algo with name partially matching given string. Remote only.

    owner (List[str]): list algo with given owners.

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list algo matching provided conditions in metadata.

    permissions (List[str]): list algo which can be used by any of the listed nodes. Remote only.
    compute_plan_key (str): list algo that are in the given compute plan. Remote only.
    dataset_key (str): list algo linked or using this dataset. Remote only.
    data_sample_key (List[str]): list algo linked or that used this data sample(s). Remote only.
## list_composite_traintuple
```text
list_composite_traintuple(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.CompositeTraintuple]
```

List composite traintuples.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.CompositeTraintuple`: the returned object is described
in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model.

``Filters allowed keys:``

    key (List[str]): list composite traintuples with listed keys.

    owner (List[str]): list composite traintuples with listed owners.

    worker (List[str]): list composite traintuples which ran on listed workers. Remote only.

    rank (List[int]): list composite traintuples which are at given ranks.

    status (str): list composite traintuples with given status.
                    Possible values: 'waiting', 'todo', 'doing', 'done', 'canceled', 'failed'

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list composite traintuples matching provided conditions in metadata. Remote only.
    compute_plan_key (str): list composite traintuples that are in the given compute plan. Remote only.
    algo_key (str): list composite traintuples that used the given algo. Remote only.
    dataset_key (str): list composite traintuples linked or using this dataset. Remote only.
    data_sample_key (List[str]): list composite traintuples linked or that used this data sample(s).
        Remote only.
## list_compute_plan
```text
list_compute_plan(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.ComputePlan]
```

List compute plans.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.ComputePlan`: the returned object is described
in the [models.ComputePlan](sdk_models.md#ComputePlan) model

``Filters allowed keys:``

    key (List[str]): list compute plans with listed keys.

    name (str): list compute plans with name partially matching given string. Remote only.

    owner (List[str]): list compute plans with listed owners.

    worker (List[str]): list compute plans which ran on listed workers. Remote only.

    status (str): list compute plans with given status.
                    Possible values: 'waiting', 'todo', 'doing', 'done', 'canceled', 'failed'

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list compute plans matching provided conditions in metadata. Remote only.
    algo_key (str): list compute plans that used the given algo. Remote only.
    dataset_key (str): list compute plans linked or using this dataset. Remote only.
    data_sample_key (List[str]): list compute plans linked or that used this data sample(s). Remote only.
## list_data_sample
```text
list_data_sample(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.DataSample]
```

List data samples.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.DataSample`: the returned object is described
in the [models.DataSample](sdk_models.md#DataSample) model

``Filters allowed keys:``

    key (List[str]): list data samples with listed keys.

    owner (List[str]): list data samples with listed owners.
    compute_plan_key (str): list data samples that are in the given compute plan. Remote only.
    algo_key (str): list data samples that used the given algo. Remote only.
    dataset_key (str): list data samples linked or using this dataset. Remote only.
## list_dataset
```text
list_dataset(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.Dataset]
```

List datasets.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**

 - `models.Dataset`: the returned object is described
in the [models.Dataset](sdk_models.md#Dataset) model

``Filters allowed keys:``

    key (List[str]): list dataset with given keys.

    name (str): list dataset with name partially matching given string. Remote only.

    owner (List[str]): list dataset with given owners.

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list dataset matching provided conditions in metadata.

    permissions (List[str]) : list dataset which can be used by any of the listed nodes. Remote only.
    compute_plan_key (str): list dataset that are in the given compute plan. Remote only.
    algo_key (str): list dataset that used the given algo. Remote only.
    data_sample_key (List[str]): list dataset linked or that used this data sample(s). Remote only.
## list_metric
```text
list_metric(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.Metric]
```

List metrics.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**

 - `models.Metric`: the returned object is described
in the [models.Metric](sdk_models.md#Metric) model

``Filters allowed keys:``

    key (List[str]): list metrics with given keys.

    name (str): list metrics with name partially matching given string. Remote only.

    owner (List[str]): list metrics with given owners.

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list metrics matching provided conditions in metadata.

    permissions (List[str]) : list metrics which can be used by any of the listed nodes. Remote only.
    compute_plan_key (str): list metrics that are in the given compute plan. Remote only.
    dataset_key (str): list metrics linked or using this dataset. Remote only.
    data_sample_key (List[str]): list metrics linked or that used this data sample(s). Remote only.
## list_organization
```text
list_organization(self, *args, **kwargs) -> List[substra.sdk.models.Organization]
```

List organizations, the returned object is described
in the [models.Organization](sdk_models.md#Organization) model
## list_testtuple
```text
list_testtuple(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.Testtuple]
```

List testtuples.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.Testtuple`: the returned object is described
in the [models.Testtuple](sdk_models.md#Testtuple) model

``Filters allowed keys:``

    key (List[str]): list testtuples with listed keys.

    owner (List[str]): list testtuples with listed owners.

    worker (List[str]): list testtuples which ran on listed workers. Remote only.

    rank (List[int]): list testtuples which are at given ranks.

    status (str): list testtuples with given status.
                    Possible values: 'waiting', 'todo', 'doing', 'done', 'canceled', 'failed'

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list testtuples matching provided conditions in metadata. Remote only.
    compute_plan_key (str): list testtuples that are in the given compute plan. Remote only.
    algo_key (str): list testtuples that used the given algo. Remote only.
    dataset_key (str): list testtuples linked or using this dataset. Remote only.
    data_sample_key (List[str]): list testtuples linked or that used this data sample(s). Remote only.
## list_traintuple
```text
list_traintuple(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.Traintuple]
```

List traintuples.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.Traintuple`: the returned object is described
in the [models.Traintuple](sdk_models.md#Traintuple) model

``Filters allowed keys:``

    key (List[str]): list traintuples with listed keys.

    owner (List[str]): list traintuples with listed owners.

    worker (List[str]): list traintuples which ran on listed workers. Remote only.

    rank (List[int]): list traintuples which are at given ranks.

    status (str): list traintuples with given status.
                    Possible values: 'waiting', 'todo', 'doing', 'done', 'canceled', 'failed'

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list traintuples matching provided conditions in metadata. Remote only.
    compute_plan_key (str): list traintuples that are in the given compute plan. Remote only.
    algo_key (str): list traintuples that used the given algo. Remote only.
    dataset_key (str): list traintuples linked or using this dataset. Remote only.
    data_sample_key (List[str]): list traintuples linked or that used this data sample(s). Remote only.
## login
```text
login(self, username, password)
```

Login to a remote server.
## organization_info
```text
organization_info(self) -> dict
```

Get organization information.
## update_compute_plan
```text
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
```text
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
