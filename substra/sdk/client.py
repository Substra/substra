import dataclasses
import functools
import logging
import os
import pathlib
import time
from collections.abc import Callable
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Union

import yaml
from slugify import slugify

from substra.sdk import backends
from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.utils import check_and_format_search_filters
from substra.sdk.utils import check_search_ordering
from substra.sdk.utils import is_valid_uuid

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60
DEFAULT_BATCH_SIZE = 500
DEFAULT_BACKEND_TYPE = schemas.BackendType.LOCAL_SUBPROCESS

# Temporary output identifiers, to be removed once user can pass its own identifiers
MODEL_OUTPUT_IDENTIFIER = "model"
HEAD_OUTPUT_IDENTIFIER = "local"
TRUNK_OUTPUT_IDENTIFIER = "shared"


def logit(f):
    """Decorator used to log all high-level methods of the Substra client."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug(f"{f.__name__}: call")
        ts = time.time()
        error = None
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error = e.__class__.__name__
            raise
        finally:
            # add a log even if the function raises an exception
            te = time.time()
            elapsed = (te - ts) * 1000
            logger.info(f"{f.__name__}: done in {elapsed:.2f}ms; error={error}")

    return wrapper


def _upper_slug(s: str) -> str:
    return slugify(s, separator="_").upper()


def _get_env_var(attribute_name: str, client_name: str) -> str:
    """
    Returns the environment variable associated with a given attribute for a given Client,
    identified by its client_name
    """
    return f"SUBSTRA_{_upper_slug(client_name)}_{_upper_slug(attribute_name)}"


@dataclasses.dataclass
class SettingValue:
    value: Any
    origin: Literal["code", "environment_variable", "config_file", "default"]


def _get_config_value(
    *,
    attribute_name: str,
    code_values: Dict[str, Any],
    client_name: Optional[str],
    client_config_dict: Dict[str, str],
    mapping: Dict[str, Callable],
) -> SettingValue:
    """
    For a given attribute, return the value to be used in the Client configuration.
    The order of precedence is: values defined by the user in the code, environment variables, values read from the
    configuration file. If the attribute is not set, the value returned is None (and the origin is set to "default").

    Args:
        attribute_name (str): Name of the attribute for which we want to get the value to use
        code_values (dict): Dictionary containing the values read from the code (or None)
        client_name (str or None): Name of the client; it is used to determine which env var to use and which
            sub-dictionary of the configuration file to consider; if None, only the values defined in the code
            are considered.
        client_config_dict (dict): Content of the configuration file
        mapping (dict): Mapping associating a callable to each attribute; usually used for type conversion, but could be
            used for more advanced processing

    Returns:
        SettingValue: Object containing the value and its origin (code, environment_variable, config_file or default)
    """

    # Some values are boolean that might be set to False, so we check explicitly "is not None"
    # Note that explicitly passing "None" in the code is equivalent to omitting it.
    # (code_values will actually always contain all the keys, with None values for keys that were omitted)
    if code_values.get(attribute_name) is not None:
        return SettingValue(value=code_values[attribute_name], origin="code")

    # if client_name is not given, we cannot look through env var and config files
    if not client_name:
        return SettingValue(value=None, origin="default")

    env_var_name = _get_env_var(attribute_name, client_name)
    # In environment variables, though, we never get "None"
    if env_var_name in os.environ:
        return SettingValue(value=mapping[attribute_name](os.environ[env_var_name]), origin="environment_variable")

    if attribute_name in client_config_dict:
        return SettingValue(value=mapping[attribute_name](client_config_dict[attribute_name]), origin="config_file")

    return SettingValue(value=None, origin="default")


def get_client_configuration(
    *,
    config_file: Optional[pathlib.Path],
    client_name: Optional[str],
    code_values: Dict[str, Any],
) -> Dict[str, SettingValue]:
    """
    Get the unified configuration values for a given client, out of three possible sources.
    The order of precedence is: values defined by the user in the code, environment variables, values read from the
    configuration file. If the attribute is not set, the value returned is None (and the origin is set to "default").

    Args:
        config_file (Path or None): Path to the yaml configuration file, if existing
        client_name (str or None): Name of the client; it is used to determine which env var to use and which
            sub-dictionary of the configuration file to consider; if None, only the values defined in the code
            are considered.
        code_values (dict): Value passed by the user directly in the code when instantiating the `Client`

    Returns:
     A dictionary associating each attribute with its `SettingValue` (containing the actual value and its origin)

    """
    if config_file and config_file.exists():
        config_dict = yaml.safe_load(config_file.read_text(encoding=None))
    else:
        config_dict = {}

    values_mapping = {
        "url": str,
        "token": str,
        "username": str,
        "password": str,
        "retry_timeout": int,
        "insecure": bool,
        "backend_type": schemas.BackendType,
    }
    return {
        attribute_name: _get_config_value(
            attribute_name=attribute_name,
            code_values=code_values,
            client_name=client_name,
            client_config_dict=config_dict.get(client_name, {}),
            mapping=values_mapping,
        )
        for attribute_name in values_mapping
    }


class Client:
    """Create a client.
    Defaults to a subprocess client, suitable for development purpose.
    Configuration can be passed in the code, through environment variables or through a configuration file.
    The order of precedence is: values defined by the user in the code, environment variables, values read from the
    configuration file. If the attribute is not set, the value returned is None (and the origin is set to "default").
    In order to use configuration values not explicitly defined in the code, the parameter `client_name` must
    not be None.

    Args:
        client_name (str, optional): Name of the client.
            Used to load relevant environment variables and select the right dictionary in the configuration file.
            Defaults to None.
        configuration_file (path, optional): Path to te configuration file.
            `client_name` must be defined too.
            Defaults to None.
        url (str, optional): URL of the Substra platform.
            Mandatory to connect to a Substra platform. If no URL is given, all assets are created locally.
            Can be set to "" to remove any previously defined URL (in a configuration file or environment variable).
            Defaults to None.
        token (str, optional): Token to authenticate to the Substra platform.
            If no token is given, and a `username`/ `password` pair is provided,  the Client will try to authenticate
            using 'login' function. It's always possible to generate a new token later by making another call to the
            `login` function.
            Defaults to None.
        username (str, optional): Username to authenticate to the Substra platform.
            Used in conjunction with a password to generate a token if not given, using the `login` function.

            If using username/password, you should use a context manager to ensure the session terminates as intended:
            ```
            with Client(username, password) as client:
               ...
            ```
            Not stored.
            Defaults to None.
        password (str, optional): Password to authenticate to the Substra platform.
            Used in conjunction with a username to generate a token if not given, using the `login` function.
            Not stored.
            Defaults to None.
        retry_timeout (int, optional): Number of seconds before attempting a retry call in case of timeout.
            Defaults to 5 minutes.
        insecure (bool, optional): If True, the client can call a not-certified backend.
            This is for development purposes.
            Defaults to False.
        backend_type (schemas.BackendType, optional): Which backend type to use.
            Possible values are `remote`, `docker` and `subprocess`.
            Defaults to `subprocess`.
            In `remote` mode, assets are registered on a deployed platform which also executes the tasks.
            In `subprocess` or `docker` mode, if no URL is given then all assets are created locally and tasks are
            executed locally. If a URL is given then the mode is a hybrid one: new assets are
            created locally but can access assets from the deployed Substra platform. The platform is in read-only mode
            and tasks are executed locally.
    """

    def __init__(
        self,
        *,
        client_name: Optional[str] = None,
        configuration_file: Optional[pathlib.Path] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        retry_timeout: Optional[int] = None,
        insecure: Optional[bool] = None,
        backend_type: Optional[schemas.BackendType] = None,
    ):
        # The value "" (which is Falsy) is used to bypass configuration file
        if configuration_file is None:
            configuration_file = os.getenv("SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH")

            if configuration_file:
                logger.info(
                    "Configuration file path set from env var SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH: "
                    f"'{configuration_file}'"
                )

        if configuration_file and not client_name:
            raise exceptions.ConfigurationInfoError(
                "Configuration file cannot be used because no `client_name` was given."
            )

        if configuration_file:
            configuration_file = pathlib.Path(configuration_file)

        code_values = {
            "url": url,
            "token": token,
            "username": username,
            "password": password,
            "retry_timeout": retry_timeout,
            "insecure": insecure,
            "backend_type": backend_type,
        }
        config_dict = get_client_configuration(
            client_name=client_name, config_file=configuration_file, code_values=code_values
        )
        if config_dict["backend_type"].value is None:
            logger.info("No backend type specified, defaulting to subprocess")
            backend_type = DEFAULT_BACKEND_TYPE
        else:
            backend_type = config_dict["backend_type"].value
            logger.info(f"Backend type set to {backend_type}, " f"as defined in {config_dict['backend_type'].origin}")

        self._url = config_dict["url"].value
        if self._url:
            logger.info(
                f"The parameter `url` has been set to {self._url} " f"as defined in {config_dict['url'].origin} "
            )
        else:
            logger.info("No URL has been given, all assets will be created locally.")

        self._token = config_dict["token"].value
        if self._token:
            logger.info(f"Token read from {config_dict['token'].origin}")

        self._retry_timeout = (
            config_dict["retry_timeout"].value
            if config_dict["retry_timeout"].value is not None
            else DEFAULT_RETRY_TIMEOUT
        )
        logger.info(
            f"The parameter `retry_timeout` has been set to {self._retry_timeout} "
            f"as defined in {config_dict['retry_timeout'].origin} "
        )

        self._insecure = config_dict["insecure"].value if config_dict["insecure"].value is not None else False

        logger.info(
            f"The parameter `insecure` has been set to {self._insecure} "
            f"as defined in {config_dict['insecure'].origin} "
        )

        self._backend = self._get_backend(backend_type)
        if (
            self._url
            and self._token is None
            and not (config_dict["username"].value is None or config_dict["password"].value is None)
        ):
            logger.info(
                f"No token provided, getting one using username set in {config_dict['username'].origin} "
                f"and password set in {config_dict['password'].origin}"
            )
            self._token = self.login(config_dict["username"].value, config_dict["password"].value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def __del__(self):
        self.logout()

    def _get_backend(self, backend_type: schemas.BackendType):
        # Three possibilities:
        # - remote: get a remote backend
        # - subprocess/docker and no url is defined: fully local backend
        # - subprocess/docker and url is defined: local backend that connects to
        #                           a deployed backend (read-only)
        if backend_type == schemas.BackendType.REMOTE:
            return backends.get(
                schemas.BackendType.REMOTE,
                url=self._url,
                insecure=self._insecure,
                token=self._token,
                retry_timeout=self._retry_timeout,
            )
        if backend_type in [schemas.BackendType.LOCAL_DOCKER, schemas.BackendType.LOCAL_SUBPROCESS]:
            backend = None
            if self._url:
                backend = backends.get(
                    schemas.BackendType.REMOTE,
                    url=self._url,
                    insecure=self._insecure,
                    token=self._token,
                    retry_timeout=self._retry_timeout,
                )
            return backends.get(
                backend_type,
                backend,
            )
        raise exceptions.SDKException(
            f"Unknown value for the execution mode: {backend_type}, "
            f"valid values are: {schemas.BackendType.__members__.values()}"
        )

    @property
    def temp_directory(self):
        """Temporary directory for storing assets in local mode.
        Deleted when the client is deleted.
        """
        if isinstance(self._backend, backends.Local):
            return self._backend.temp_directory

    @property
    def backend_mode(self) -> schemas.BackendType:
        """Get the backend mode.

        Returns:
            str: Backend mode
        """
        return self._backend.backend_mode

    @logit
    def login(self, username, password):
        """Login to a remote server."""
        if not self._backend:
            raise exceptions.SDKException("No backend found")
        self._token = self._backend.login(username, password)
        return self._token

    @logit
    def logout(self) -> None:
        """
        Log out from a remote server, if Client.login was used
        (otherwise, nothing happens)
        """
        if not self._backend:
            raise exceptions.SDKException("No backend found")
        self._backend.logout()
        self._token = None

    @staticmethod
    def _get_spec(asset_type, data):
        if isinstance(data, asset_type):
            return data
        return asset_type(**data)

    @logit
    def add_data_sample(self, data: Union[dict, schemas.DataSampleSpec], local: bool = True) -> str:
        """Create a new data sample asset and return its key.

        Args:
            data (Union[dict, schemas.DataSampleSpec]): data sample to add. If it is a dict,
                it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).
            local (bool, optional): If `local` is true, `path` must refer to a directory located
                on the local filesystem. The file content will be transferred to the server
                through an HTTP query, so this mode should be used for relatively small files
                (<10mo).

                If `local` is false, `path` must refer to a directory located on the server
                filesystem. This directory must be accessible (readable) by the server.  This
                mode is well suited for all kind of file sizes. Defaults to True.

        Returns:
            str: key of the data sample
        """
        spec = self._get_spec(schemas.DataSampleSpec, data)
        if spec.paths:
            raise ValueError("data: invalid 'paths' field")
        if not spec.path:
            raise ValueError("data: missing 'path' field")
        spec_options = {
            "local": local,
        }
        return self._backend.add(spec, spec_options=spec_options)

    @logit
    def add_data_samples(
        self,
        data: Union[dict, schemas.DataSampleSpec],
        local: bool = True,
    ) -> List[str]:
        """Create many data sample assets and return  a list of keys.

        Create multiple data samples through a single HTTP request.
        This method is well suited for adding multiple small files only. For adding a
        large amount of data it is recommended to add them one by one. It allows a
        better control in case of failures.

        Args:
            data (Union[dict, schemas.DataSampleSpec]): data samples to add. If it is a dict,
                it must follow the [DataSampleSpec schema](sdk_schemas.md#DataSampleSpec).
                The `paths` in the data dictionary must be a list of paths where each path
                points to a directory representing one data sample.
            local (bool, optional):  Please refer to the method `Client.add_data_sample`.
                Defaults to True.

        Returns:
            List[str]: List of the data sample keys
        """
        spec = self._get_spec(schemas.DataSampleSpec, data)
        if spec.path:
            raise ValueError("data: invalid 'path' field")
        if not spec.paths:
            raise ValueError("data: missing 'paths' field")
        spec_options = {
            "local": local,
        }
        return self._backend.add(
            spec,
            spec_options=spec_options,
        )

    @logit
    def add_dataset(self, data: Union[dict, schemas.DatasetSpec]):
        """Create new dataset asset and return its key.

        Args:
            data (Union[dict, schemas.DatasetSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

        Returns:
            str: Key of the dataset
        """
        spec = self._get_spec(schemas.DatasetSpec, data)
        return self._backend.add(spec)

    @logit
    def add_function(self, data: Union[dict, schemas.FunctionSpec]) -> str:
        """Create new function asset.

        Args:
            data (Union[dict, schemas.FunctionSpec]): If it is a dict, it must have the same keys
                as specified in [schemas.FunctionSpec](sdk_schemas.md#FunctionSpec).

        Returns:
            str: Key of the function
        """
        spec = self._get_spec(schemas.FunctionSpec, data)
        return self._backend.add(spec)

    @logit
    def add_task(self, data: Union[dict, schemas.TaskSpec]) -> str:
        """Create new task asset.

        Args:
            data (Union[dict, schemas.TaskSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.TaskSpec](sdk_schemas.md#TaskSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.TaskSpec, data)
        return self._backend.add(spec)

    @logit
    def add_compute_plan(
        self,
        data: Union[dict, schemas.ComputePlanSpec],
        auto_batching: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> models.ComputePlan:
        """Create new compute plan asset.

        Args:
            data (Union[dict, schemas.ComputePlanSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.ComputePlanSpec](sdk_schemas.md#ComputePlanSpec).
            auto_batching (bool, optional): Set 'auto_batching' to False to upload all the tasks of
                the compute plan at once. Defaults to True.
            batch_size (int, optional): If 'auto_batching' is True, change `batch_size` to define
                the number of tasks uploaded in each batch (default 500).

        Returns:
            models.ComputePlan: Created compute plan
        """
        spec = self._get_spec(schemas.ComputePlanSpec, data)
        spec_options = {
            "auto_batching": auto_batching,
            "batch_size": batch_size,
        }

        if not is_valid_uuid(spec.key):
            raise exceptions.ComputePlanKeyFormatError(
                "The compute plan key has to respect the UUID format. You can use the uuid library to generate it. \
            Example: compute_plan_key=str(uuid.uuid4())"
            )

        return self._backend.add(spec, spec_options=spec_options)

    @logit
    def get_function(self, key: str) -> models.Function:
        """Get function by key, the returned object is described
        in the [models.Function](sdk_models.md#Function) model"""
        return self._backend.get(schemas.Type.Function, key)

    @logit
    def get_compute_plan(self, key: str) -> models.ComputePlan:
        """Get compute plan by key, the returned object is described
        in the [models.ComputePlan](sdk_models.md#ComputePlan) model"""
        return self._backend.get(schemas.Type.ComputePlan, key)

    @logit
    def get_performances(self, key: str, *, wait_completion: bool = False) -> models.Performances:
        """Get the compute plan performances by key, the returned object is described
        in the [models.Performances](sdk_models.md#Performances) and easily convertible
        to pandas dataframe. You can wait for compute task to finish by setting
        `wait_completion = True`

        Example:
            ```python
            perf = client.get_performances(cp_key)
            df = pd.DataFrame(perf.model_dump())
            print(df)
            ```
        """
        if wait_completion:
            self.wait_compute_plan(key)
        performances = self._backend.get_performances(key)
        return performances

    @logit
    def get_dataset(self, key: str) -> models.Dataset:
        """Get dataset by key, the returned object is described
        in the [models.Dataset](sdk_models.md#Dataset) model"""
        return self._backend.get(schemas.Type.Dataset, key)

    @logit
    def get_task(self, key: str) -> models.Task:
        """Get task by key, the returned object is described
        in the [models.Task](sdk_models.md#Task) model"""
        return self._backend.get(schemas.Type.Task, key)

    @logit
    def get_logs(self, task_key: str) -> str:
        """Get task logs by task key, the returned object is a string
        containing the logs.

        Logs are only available for tasks that experienced an execution failure.
        Attempting to retrieve logs for tasks in any other states or for non-existing
        tasks will result in a NotFound error.
        """
        return self._backend.download_logs(task_key, destination_file=None)

    @logit
    def get_model(self, key: str) -> models.OutModel:
        return self._backend.get(schemas.Type.Model, key)

    @logit
    def list_model(self, filters: dict = None, ascending: bool = False) -> List[models.OutModel]:
        """List models.

        The ``filters`` argument is a dictionnary, with those possible keys:\n
            key (list[str]): list model with given keys.\n
            compute_task_key (list[str]): list model produced by this compute task.\n
            owner (list[str]): list model with given owners.\n
            permissions (list[str]): list models which can be used by any of the listed nodes. Remote mode only.\n

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            ascending (bool, optional): Sorts results by oldest creation_date first. Default False (descending order).

        Returns:
            models.OutModel the returned object is described in the [models.OutModel](sdk_models.md#OutModel) model"""
        return self._list(schemas.Type.Model, filters, "creation_date", ascending)

    @logit
    def get_data_sample(self, key: str) -> models.DataSample:
        """Get data sample by key, the returned object is described
        in the [models.Datasample](sdk_models.md#DataSample) model"""
        return self._backend.get(schemas.Type.DataSample, key)

    def _list(
        self, asset_type, filters: dict = None, order_by: str = None, ascending: bool = False, paginated: bool = True
    ):
        filters = check_and_format_search_filters(asset_type, filters)
        check_search_ordering(order_by)
        return self._backend.list(asset_type, filters, order_by, ascending)

    @logit
    def list_function(self, filters: dict = None, ascending: bool = False) -> List[models.Function]:
        """List functions.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list function with given keys.\n
            name (str): list function with name partially matching given string. Remote mode only.\n
            owner (List[str]): list function with given owners.\n
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list function matching provided conditions in metadata.\n
            permissions (List[str]): list function which can be used by any of the listed nodes. Remote mode only.
            compute_plan_key (str): list function that are in the given compute plan. Remote mode only.
            dataset_key (str): list function linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list function linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            ascending (bool, optional): Sorts results by oldest creation_date first. Default False (descending order).

        Returns:
            models.Function: the returned object is described in the [models.Function](sdk_models.md#Function) model

        """

        return self._list(schemas.Type.Function, filters, "creation_date", ascending)

    @logit
    def list_compute_plan(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.ComputePlan]:
        """List compute plans.

         The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list compute plans with listed keys.\n
            name (str): list compute plans with name partially matching given string. Remote mode only.\n
            owner (List[str]): list compute plans with listed owners.\n
            worker (List[str]): list compute plans which ran on listed workers. Remote mode only.\n
            status (List[str]): list compute plans with given status.
                The possible values are the values of `substra.models.ComputePlanStatus`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list compute plans matching provided conditions in metadata. Remote mode only.
            function_key (str): list compute plans that used the given function. Remote mode only.
            dataset_key (str): list compute plans linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list compute plans linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.ComputePlan: the returned object is described
        in the [models.ComputePlan](sdk_models.md#ComputePlan) model
        """

        return self._list(schemas.Type.ComputePlan, filters, order_by, ascending)

    @logit
    def list_data_sample(self, filters: dict = None, ascending: bool = False) -> List[models.DataSample]:
        """List data samples.

            The ``filters`` argument is a dictionary, with those possible keys:\n
                key (List[str]): list data samples with listed keys.
                owner (List[str]): list data samples with listed owners.
                compute_plan_key (str): list data samples that are in the given compute plan. Remote mode only.
                function_key (str): list data samples that used the given function. Remote mode only.
                dataset_key (str): list data samples linked or using this dataset. Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.DataSample: the returned object is described in the
                [models.DataSample](sdk_models.md#DataSample) model
        """
        return self._list(schemas.Type.DataSample, filters, "creation_date", ascending)

    @logit
    def list_dataset(self, filters: dict = None, ascending: bool = False) -> List[models.Dataset]:
        """List datasets.

         The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list dataset with given keys.\n
            name (str): list dataset with name partially matching given string. Remote mode only.\n
            owner (List[str]): list dataset with given owners.\n
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list dataset matching provided conditions in metadata.\n
            permissions (List[str]) : list dataset which can be used by any of the listed nodes. Remote mode only.
            compute_plan_key (str): list dataset that are in the given compute plan. Remote mode only.
            function_key (str): list dataset that used the given function. Remote mode only.
            data_sample_key (List[str]): list dataset linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            ascending (bool, optional): Sorts results by oldest creation_date first. Default False (descending order).

        Returns:
            models.Dataset: the returned object is described
        in the [models.Dataset](sdk_models.md#Dataset) model


        """

        return self._list(schemas.Type.Dataset, filters, "creation_date", ascending)

    @logit
    def list_task(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.Task]:
        """List tasks.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list tasks with listed keys.\n
            owner (List[str]): list tasks with listed owners.\n
            worker (List[str]): list tasks which ran on listed workers. Remote mode only.\n
            rank (List[int]): list tasks which are at given ranks.\n
            status (List[str]): list tasks with given status.
                The possible values are the values of `substra.models.ComputeTaskStatus`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list tasks matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list tasks that are in the given compute plan. Remote mode only.
            function_key (str): list tasks that used the given function. Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.Task: the returned object is described in the
                [models.Task](sdk_models.md#Task) model


        """
        return self._list(schemas.Type.Task, filters, order_by, ascending)

    @logit
    def list_task_input_assets(self, key: str) -> List[models.InputAsset]:
        """List input assets for a specific task, the returned object is described
        in the [models.InputAsset](sdk_models.md#InputAsset) model"""
        return self._backend.list_task_input_assets(key)

    @logit
    def list_task_output_assets(self, key: str, *, wait_completion: bool = False) -> List[models.OutputAsset]:
        """List output assets for a specific task, the returned object is described
        in the [models.OutputAsset](sdk_models.md#OutputAsset) model. You can wait
        for compute task to finish by setting `wait_completion = True`"""
        if wait_completion:
            self.wait_task(key)
        return self._backend.list_task_output_assets(key)

    @logit
    def get_task_output_asset(self, key: str, identifier: str, *, wait_completion: bool = False) -> models.OutputAsset:
        """Get an output asset for a specific task with a defined identifier, the returned object is described
        in the [models.OutputAsset](sdk_models.md#OutputAsset) model. You can wait
        for compute task to finish by setting `wait_completion = True`"""
        if wait_completion:
            self.wait_task(key)
        return self._backend.get_task_output_asset(key, identifier)

    @logit
    def list_organization(self, *args, **kwargs) -> List[models.Organization]:
        """List organizations, the returned object is described
        in the [models.Organization](sdk_models.md#Organization) model"""
        # results are not paginated for organizations
        return self._backend.list(schemas.Type.Organization, paginated=False)

    @logit
    def update_function(self, key: str, name: str):
        spec = self._get_spec(schemas.UpdateFunctionSpec, {"name": name})
        self._backend.update(key, spec)
        return

    @logit
    def add_compute_plan_tasks(
        self,
        key: str,
        tasks: Union[dict, schemas.UpdateComputePlanTasksSpec],
        auto_batching: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> models.ComputePlan:
        """Update compute plan.

        Args:
            key (str): Compute plan key
            tasks (Union[dict, schemas.UpdateComputePlanTasksSpec]): If it is a dict,
                it must have the same keys as specified in
                [schemas.UpdateComputePlanTasksSpec](sdk_schemas.md#UpdateComputePlanTasksSpec).
            auto_batching (bool, optional): Set 'auto_batching' to False to upload all
                the tasks of the compute plan at once. Defaults to True.
            batch_size (int, optional): If 'auto_batching' is True, change `batch_size`
                to define the number of tasks uploaded in each batch (default 500).

        Returns:
            models.ComputePlan: updated compute plan, as described in the
            [models.ComputePlan](sdk_models.md#ComputePlan) model
        """
        if isinstance(tasks, dict):
            tasks["key"] = key
        spec = self._get_spec(schemas.UpdateComputePlanTasksSpec, tasks)
        spec_options = {
            "auto_batching": auto_batching,
            "batch_size": batch_size,
        }
        return self._backend.add_compute_plan_tasks(spec, spec_options=spec_options)

    @logit
    def update_compute_plan(self, key: str, name: str):
        spec = self._get_spec(schemas.UpdateComputePlanSpec, {"name": name})
        self._backend.update(key, spec)
        return

    @logit
    def update_dataset(self, key: str, name: str):
        spec = self._get_spec(schemas.UpdateDatasetSpec, {"name": name})
        self._backend.update(key, spec)
        return

    @logit
    def link_dataset_with_data_samples(
        self,
        dataset_key: str,
        data_sample_keys: List[str],
    ) -> List[str]:
        """Link dataset with data samples."""
        return self._backend.link_dataset_with_data_samples(dataset_key, data_sample_keys)

    @logit
    def download_dataset(self, key: str, destination_folder: str) -> pathlib.Path:
        """Download data manager resource.
        Download opener script in destination folder.

        Args:
            key (str): Dataset key to download
            destination_folder (str): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded dataset
        """
        return pathlib.Path(
            self._backend.download(
                schemas.Type.Dataset,
                "opener.storage_address",
                key,
                os.path.join(destination_folder, "opener.py"),
            )
        )

    @logit
    def download_function(self, key: str, destination_folder: str) -> pathlib.Path:
        """Download function resource.
        Download function package in destination folder.

        Args:
            key (str): Function key to download
            destination_folder (str): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded function
        """

        return pathlib.Path(
            self._backend.download(
                schemas.Type.Function,
                "archive.storage_address",
                key,
                os.path.join(destination_folder, "function.tar.gz"),
            )
        )

    @logit
    def download_model(self, key: str, destination_folder) -> pathlib.Path:
        """Download model to destination file.

        This model was saved using the 'save_model' function of the class.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        class.

        Args:
            key (str): Model key to download
            destination_folder (str): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """
        return pathlib.Path(self._backend.download_model(key, os.path.join(destination_folder, f"model_{key}")))

    @logit
    def download_model_from_task(self, task_key: str, identifier: str, folder: os.PathLike) -> pathlib.Path:
        """Download task model to destination file.

        This model was saved using the 'save_model' function of the class.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        class.

        Args:
            task_key (str): Task key to download
            identifier(str): output identifier
            folder (os.PathLike): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """
        task_output = self._backend.get_task_output_asset(task_key, identifier)
        model = task_output.asset
        return self.download_model(model.key, folder)

    @logit
    def download_logs(self, task_key: str, folder: str) -> str:
        """Download the execution logs of a failed task to a destination file.

        The logs are saved in the folder to a file named 'task_logs_{task_key}.txt'.

        Logs are only available for tasks that experienced an execution failure.
        Attempting to retrieve logs for tasks in any other states or for non-existing
        tasks will result in a NotFound error.

        Args:
            task_key: the key of the task that produced the logs
            folder: the destination directory

        Returns:
            str: The logs as a str
        """
        return self._backend.download_logs(task_key, os.path.join(folder, f"task_logs_{task_key}.txt"))

    @logit
    def describe_function(self, key: str) -> str:
        """Get function description."""
        return self._backend.describe(schemas.Type.Function, key)

    @logit
    def describe_dataset(self, key: str) -> str:
        """Get dataset description."""
        return self._backend.describe(schemas.Type.Dataset, key)

    @logit
    def organization_info(self) -> models.OrganizationInfo:
        """Get organization information."""
        return self._backend.organization_info()

    @logit
    def cancel_compute_plan(self, key: str) -> None:
        """Cancel execution of compute plan. Nothing is returned by this method"""
        self._backend.cancel_compute_plan(key)

    @logit
    def wait_compute_plan(
        self, key: str, *, timeout: Optional[float] = None, polling_period: float = 2.0, raise_on_failure: bool = True
    ) -> models.ComputePlan:
        """Wait for the execution of the given compute plan to finish.

        It is considered finished when the status is done, failed or cancelled.

        Args:
            key (str): the key of the compute plan to wait for
            timeout (float, optional): maximum time to wait, in seconds. If set to None, will hang until completion.
            polling_period (float): time to wait between two checks, in seconds. Defaults to 2.0.
            raise_on_failure (bool): whether to raise an exception if the execution fails. Defaults to True.

        Returns:
            models.ComputePlan: the compute plan after completion

        Raises:
            exceptions.FutureFailureError: The compute plan failed or have been cancelled.
            exceptions.FutureTimeoutError: The compute plan took more than the duration set in the timeout to complete.
                Not raised when `timeout == None`
        """
        asset_getter = self.get_compute_plan
        status_failed = models.ComputePlanStatus.failed.value
        status_canceled = models.ComputePlanStatus.canceled.value
        statuses_stopped = (
            models.ComputePlanStatus.done.value,
            models.ComputePlanStatus.failed.value,
            models.ComputePlanStatus.canceled.value,
        )

        return self._wait(
            key=key,
            asset_getter=asset_getter,
            polling_period=polling_period,
            raise_on_failure=raise_on_failure,
            status_canceled=status_canceled,
            status_failed=status_failed,
            statuses_stopped=statuses_stopped,
            timeout=timeout,
        )

    @logit
    def wait_task(
        self, key: str, *, timeout: Optional[float] = None, polling_period: float = 2.0, raise_on_failure: bool = True
    ) -> models.Task:
        """Wait for the execution of the given task to finish.

        It is considered finished when the status is done, failed or cancelled.

        Args:
            key (str): the key of the task to wait for.
            timeout (float, optional): maximum time to wait, in seconds. If set to None, will hang until completion.
            polling_period (float): time to wait between two checks, in seconds. Defaults to 2.0.
            raise_on_failure (bool): whether to raise an exception if the execution fails. Defaults to True.

        Returns:
            models.Task: the task after completion

         Raises:
            exceptions.FutureFailureError: The task failed or have been cancelled.
            exceptions.FutureTimeoutError: The task took more than the duration set in the timeout to complete.
                Not raised when `timeout == None`
        """
        asset_getter = self.get_task
        status_canceled = models.ComputeTaskStatus.canceled.value
        status_failed = models.ComputeTaskStatus.failed.value
        statuses_stopped = (models.ComputeTaskStatus.done.value, models.ComputeTaskStatus.canceled.value)
        return self._wait(
            key=key,
            asset_getter=asset_getter,
            polling_period=polling_period,
            raise_on_failure=raise_on_failure,
            status_canceled=status_canceled,
            status_failed=status_failed,
            statuses_stopped=statuses_stopped,
            timeout=timeout,
        )

    @logit
    def wait_function(
        self, key: str, *, timeout: Optional[float] = None, polling_period: float = 1.0, raise_on_failure: bool = True
    ) -> models.Function:
        """Wait for the build of the given function to finish.

        It is considered finished when the status is ready, failed or cancelled.

        Args:
            key (str): the key of the task to wait for.
            timeout (float, optional): maximum time to wait, in seconds. If set to None, will hang until completion.
            polling_period (float): time to wait between two checks, in seconds. Defaults to 2.0.
            raise_on_failure (bool): whether to raise an exception if the execution fails. Defaults to True.

        Returns:
            models.Function: the function once built

         Raises:
            exceptions.FutureFailureError: The function build failed or have been cancelled.
            exceptions.FutureTimeoutError: The function took more than the duration set in the timeout to build.
                Not raised when `timeout == None`
        """
        asset_getter = self.get_function
        status_canceled = models.FunctionStatus.canceled.value
        status_failed = models.FunctionStatus.failed.value
        statuses_stopped = (
            models.FunctionStatus.ready.value,
            models.FunctionStatus.canceled.value,
            models.FunctionStatus.failed.value,
        )
        return self._wait(
            key=key,
            asset_getter=asset_getter,
            polling_period=polling_period,
            raise_on_failure=raise_on_failure,
            status_canceled=status_canceled,
            status_failed=status_failed,
            statuses_stopped=statuses_stopped,
            timeout=timeout,
        )

    def _wait(
        self,
        *,
        key: str,
        asset_getter,
        polling_period: float,
        raise_on_failure: bool,
        status_failed: str,
        status_canceled: str,
        statuses_stopped: Sequence[str],
        timeout: Optional[float] = None,
    ):
        tstart = time.time()
        while True:
            asset = asset_getter(key)

            if asset.status in statuses_stopped:
                break

            if asset.status == models.ComputeTaskStatus.failed.value and asset.error_type is not None:
                # when dealing with a failed task, wait for the error_type field of the task to be set
                # i.e. wait for the registration of the failure report
                break

            if timeout and time.time() - tstart > timeout:
                raise exceptions.FutureTimeoutError(f"Future timeout on {asset}")

            time.sleep(polling_period)

        if raise_on_failure and asset.status == status_failed:
            raise exceptions.FutureFailureError(f"Future execution failed on {asset}")

        if raise_on_failure and asset.status == status_canceled:
            raise exceptions.FutureFailureError(f"Future execution canceled on {asset}")

        return asset
