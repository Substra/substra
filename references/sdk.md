# Client
```text
Client(url: Optional[str] = None, token: Optional[str] = None, retry_timeout: int = 300, insecure: bool = False, backend_type: substra.sdk.schemas.BackendType = <BackendType.REMOTE: 'remote'>)
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
 - `backend_type (schemas.BackendType, optional)`: Which mode to use.
Possible values are `remote`, `docker` and `subprocess`.
Defaults to `remote`.
In `remote`mode, assets are registered on a deployed platform which also executes the tasks.
In `subprocess` or `docker` mode, if no URL is given then all assets are created locally and tasks are
executed locally. If a URL is given then the mode is a hybrid one: new assets are
created locally but can access assets from the deployed Substra platform. The platform is in read-only mode
and tasks are executed locally.
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
        
## add_algo
```text
add_algo(self, data: Union[dict, substra.sdk.schemas.AlgoSpec]) -> str
```

Create new algo asset.

**Arguments:**
 - `data (Union[dict, schemas.AlgoSpec], required)`: If it is a dict, it must have the same keys
as specified in [schemas.AlgoSpec](sdk_schemas.md#AlgoSpec).

**Returns:**

 - `str`: Key of the algo
## add_compute_plan
```text
add_compute_plan(self, data: Union[dict, substra.sdk.schemas.ComputePlanSpec], auto_batching: bool = True, batch_size: int = 500) -> substra.sdk.models.ComputePlan
```

Create new compute plan asset.

**Arguments:**
 - `data (Union[dict, schemas.ComputePlanSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.ComputePlanSpec](sdk_schemas.md#ComputePlanSpec).
 - `auto_batching (bool, optional)`: Set 'auto_batching' to False to upload all the tuples of
the compute plan at once. Defaults to True.
 - `batch_size (int, optional)`: If 'auto_batching' is True, change `batch_size` to define
the number of tuples uploaded in each batch (default 500).

**Returns:**

 - `models.ComputePlan`: Created compute plan
## add_compute_plan_tuples
```text
add_compute_plan_tuples(self, key: str, tuples: Union[dict, substra.sdk.schemas.UpdateComputePlanTuplesSpec], auto_batching: bool = True, batch_size: int = 500) -> substra.sdk.models.ComputePlan
```

Update compute plan.

**Arguments:**
 - `key (str, required)`: Compute plan key
 - `tuples (Union[dict, schemas.UpdateComputePlanTuplesSpec], required)`: If it is a dict,
it must have the same keys as specified in
[schemas.UpdateComputePlanTuplesSpec](sdk_schemas.md#UpdateComputePlanTuplesSpec).
 - `auto_batching (bool, optional)`: Set 'auto_batching' to False to upload all
the tuples of the compute plan at once. Defaults to True.
 - `batch_size (int, optional)`: If 'auto_batching' is True, change `batch_size`
to define the number of tuples uploaded in each batch (default 500).

**Returns:**

 - `models.ComputePlan`: updated compute plan, as described in the
[models.ComputePlan](sdk_models.md#ComputePlan) model
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

**Arguments:**
 - `data (Union[dict, schemas.DatasetSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

**Returns:**

 - `str`: Key of the dataset
## add_task
```text
add_task(self, data: Union[dict, substra.sdk.schemas.TaskSpec]) -> str
```

Create new task asset.

**Arguments:**
 - `data (Union[dict, schemas.TaskSpec], required)`: If it is a dict, it must have the same
keys as specified in [schemas.TaskSpec](sdk_schemas.md#TaskSpec).

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
## download_algo
```text
download_algo(self, key: str, destination_folder: str) -> None
```

Download algo resource.
Download algo package in destination folder.

**Arguments:**
 - `key (str, required)`: Algo key to download
 - `destination_folder (str, required)`: Destination folder

**Returns:**

 - `pathlib.Path`: Path of the downloaded algo
## download_dataset
```text
download_dataset(self, key: str, destination_folder: str) -> None
```

Download data manager resource.
Download opener script in destination folder.

**Arguments:**
 - `key (str, required)`: Dataset key to download
 - `destination_folder (str, required)`: Destination folder

**Returns:**

 - `pathlib.Path`: Path of the downloaded dataset
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

 - `str`: The logs as a str
## download_model
```text
download_model(self, key: str, destination_folder) -> None
```

Download model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.

**Arguments:**
 - `key (str, required)`: Model key to download
 - `destination_folder (str, required)`: Destination folder

**Returns:**

 - `pathlib.Path`: Path of the downloaded model
## download_model_from_task
```text
download_model_from_task(self, task_key: str, identifier: str, folder: os.PathLike) -> pathlib.Path
```

Download task model to destination file.
This model was saved using the 'save_model' function of the algorithm.
To load and use the model, please refer to the 'load_model' and 'predict' functions of the
algorithm.

**Arguments:**
 - `task_key (str, required)`: Task key to download
 - `identifier (str, required)`: output identifier
 - `folder (os.PathLike, required)`: Destination folder

**Returns:**

 - `pathlib.Path`: Path of the downloaded model
## from_config_file
```text
from_config_file(profile_name: str = 'default', config_path: Union[str, pathlib.Path] = '~/.substra', tokens_path: Union[str, pathlib.Path] = '~/.substra-tokens', token: Optional[str] = None, retry_timeout: int = 300, backend_type: substra.sdk.schemas.BackendType = <BackendType.REMOTE: 'remote'>)
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
 - `backend_type (schemas.BackendType, optional)`: Which mode to use.
Possible values are `remote`, `docker` and `subprocess`.
Defaults to `remote`.
In `remote`mode, assets are registered on a deployed platform which also executes the tasks.
In `subprocess` or `docker` mode, if no URL is given then all assets are created locally and tasks are
executed locally. If a URL is given then the mode is a hybrid one: new assets are
created locally but can access assets from the deployed Substra platform. The platform is in read-only
mode and tasks are executed locally.

**Returns:**

 - `Client`: The new client.
## get_algo
```text
get_algo(self, key: str) -> substra.sdk.models.Algo
```

Get algo by key, the returned object is described
in the [models.Algo](sdk_models.md#Algo) model
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
## get_task
```text
get_task(self, key: str) -> substra.sdk.models.Task
```

Get task by key, the returned object is described
in the [models.Task](sdk_models.md#Task) model
## link_dataset_with_data_samples
```text
link_dataset_with_data_samples(self, dataset_key: str, data_sample_keys: List[str]) -> List[str]
```

Link dataset with data samples.
## list_algo
```text
list_algo(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.Algo]
```

List algos.
The ``filters`` argument is a dictionary, with those possible keys:

    key (List[str]): list algo with given keys.

    name (str): list algo with name partially matching given string. Remote mode only.

    owner (List[str]): list algo with given owners.

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list algo matching provided conditions in metadata.

    permissions (List[str]): list algo which can be used by any of the listed nodes. Remote mode only.
    compute_plan_key (str): list algo that are in the given compute plan. Remote mode only.
    dataset_key (str): list algo linked or using this dataset. Remote mode only.
    data_sample_key (List[str]): list algo linked or that used this data sample(s). Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**

 - `models.Algo`: the returned object is described in the [models.Algo](sdk_models.md#Algo) model
## list_compute_plan
```text
list_compute_plan(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.ComputePlan]
```

List compute plans.
The ``filters`` argument is a dictionary, with those possible keys:

    key (List[str]): list compute plans with listed keys.

    name (str): list compute plans with name partially matching given string. Remote mode only.

    owner (List[str]): list compute plans with listed owners.

    worker (List[str]): list compute plans which ran on listed workers. Remote mode only.

    status (List[str]): list compute plans with given status.
        The possible values are the values of `substra.models.ComputePlanStatus`
    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list compute plans matching provided conditions in metadata. Remote mode only.
    algo_key (str): list compute plans that used the given algo. Remote mode only.
    dataset_key (str): list compute plans linked or using this dataset. Remote mode only.
    data_sample_key (List[str]): list compute plans linked or that used this data sample(s). Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.ComputePlan`: the returned object is described
## list_data_sample
```text
list_data_sample(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.DataSample]
```

List data samples.
The ``filters`` argument is a dictionary, with those possible keys:

        key (List[str]): list data samples with listed keys.
        owner (List[str]): list data samples with listed owners.
        compute_plan_key (str): list data samples that are in the given compute plan. Remote mode only.
        algo_key (str): list data samples that used the given algo. Remote mode only.
        dataset_key (str): list data samples linked or using this dataset. Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.DataSample`: the returned object is described in the
[models.DataSample](sdk_models.md#DataSample) model
## list_dataset
```text
list_dataset(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.Dataset]
```

List datasets.
The ``filters`` argument is a dictionary, with those possible keys:

    key (List[str]): list dataset with given keys.

    name (str): list dataset with name partially matching given string. Remote mode only.

    owner (List[str]): list dataset with given owners.

    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list dataset matching provided conditions in metadata.

    permissions (List[str]) : list dataset which can be used by any of the listed nodes. Remote mode only.
    compute_plan_key (str): list dataset that are in the given compute plan. Remote mode only.
    algo_key (str): list dataset that used the given algo. Remote mode only.
    data_sample_key (List[str]): list dataset linked or that used this data sample(s). Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**

 - `models.Dataset`: the returned object is described
## list_model
```text
list_model(self, filters: dict = None, ascending: bool = False) -> List[substra.sdk.models.OutModel]
```

List models.
The ``filters`` argument is a dictionnary, with those possible keys:

    key (list[str]): list model with given keys.

    compute_task_key (list[str]): list model produced by this compute task.

    owner (list[str]): list model with given owners.

    permissions (list[str]): list models which can be used by any of the listed nodes. Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `ascending (bool, optional)`: Sorts results by oldest creation_date first. Default False (descending order).

**Returns:**
models.OutModel the returned object is described in the [models.OutModel](sdk_models.md#OutModel) model
## list_organization
```text
list_organization(self, *args, **kwargs) -> List[substra.sdk.models.Organization]
```

List organizations, the returned object is described
in the [models.Organization](sdk_models.md#Organization) model
## list_task
```text
list_task(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.Task]
```

List tasks.
The ``filters`` argument is a dictionary, with those possible keys:

    key (List[str]): list tasks with listed keys.

    owner (List[str]): list tasks with listed owners.

    worker (List[str]): list tasks which ran on listed workers. Remote mode only.

    rank (List[int]): list tasks which are at given ranks.

    status (List[str]): list tasks with given status.
        The possible values are the values of `substra.models.Status`
    metadata (dict)
        {
            "key": str # the key of the metadata to filter on
            "type": "is", "contains" or "exists" # the type of query that will be used
            "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
        }: list tasks matching provided conditions in metadata. Remote mode only.
    compute_plan_key (str): list tasks that are in the given compute plan. Remote mode only.
    algo_key (str): list tasks that used the given algo. Remote mode only.

**Arguments:**
 - `filters (dict, optional)`: List of key values pair to filter on. Default None.
 - `order_by (str, optional)`: Field to sort results by.
Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
 - `ascending (bool, optional)`: Sorts results on order_by by ascending order. Default False (descending order).

**Returns:**

 - `models.Task`: the returned object is described in the
[models.Task](sdk_models.md#Task) model
## login
```text
login(self, username, password)
```

Login to a remote server.
## organization_info
```text
organization_info(self) -> substra.sdk.models.OrganizationInfo
```

Get organization information.
## update_algo
```text
update_algo(self, key: str, name: str)
```

None
## update_compute_plan
```text
update_compute_plan(self, key: str, name: str)
```

None
## update_dataset
```text
update_dataset(self, key: str, name: str)
```

None
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
