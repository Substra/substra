import functools
import logging
import os
import pathlib
import time
from typing import List
from typing import Optional
from typing import Union

from substra.sdk import backends
from substra.sdk import config as cfg
from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.utils import check_and_format_search_filters
from substra.sdk.utils import check_search_ordering
from substra.sdk.utils import is_valid_uuid

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60
DEFAULT_BATCH_SIZE = 500

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


class Client:
    """Create a client

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
        insecure (bool, optional): If True, the client can call a not-certified backend. This is
            for development purposes.
            Defaults to False.
        backend_type (schemas.BackendType, optional): Which mode to use. Defaults to deployed.
            In deployed mode, assets are registered on a deployed platform which also executes the tasks.
            In local mode (subprocess or docker), if no URL is given then all assets are created locally and tasks are
            executed locally.
            In local mode (subprocess or docker), if a URL is given then the mode is a hybrid one: new assets are
            created locally but can access assets from the deployed Substra platform. The platform is in read-only mode
            and tasks are executed locally.
            The local mode is either docker or subprocess mode: `docker` if you want the tasks to
            be executed in containers (default) or `subprocess` to execute them in Python subprocesses (faster,
            experimental: The `Dockerfile` commands are not executed, requires dependencies to be installed locally).
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        retry_timeout: int = DEFAULT_RETRY_TIMEOUT,
        insecure: bool = False,
        backend_type: schemas.BackendType = schemas.BackendType.REMOTE,
    ):
        self._retry_timeout = retry_timeout
        self._token = token

        self._insecure = insecure
        self._url = url

        self._backend = self._get_backend(backend_type)

    def _get_backend(self, backend_type: schemas.BackendType):
        # Three possibilities:
        # - deployed: get a deployed backend
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
        """Temporary directory for storing assets in debug mode.
        Deleted when the client is deleted.
        """
        if isinstance(self._backend, backends.Local):
            return self._backend.temp_directory

    @property
    def backend_mode(self) -> schemas.BackendType:
        """Get the backend mode: deployed,
        local and which type of local mode

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

    @staticmethod
    def _get_spec(asset_type, data):
        if isinstance(data, asset_type):
            return data
        return asset_type(**data)

    @classmethod
    def from_config_file(
        cls,
        profile_name: str = cfg.DEFAULT_PROFILE_NAME,
        config_path: Union[str, pathlib.Path] = cfg.DEFAULT_PATH,
        tokens_path: Union[str, pathlib.Path] = cfg.DEFAULT_TOKENS_PATH,
        token: Optional[str] = None,
        retry_timeout: int = DEFAULT_RETRY_TIMEOUT,
        backend_type: schemas.BackendType = schemas.BackendType.REMOTE,
    ):
        """Returns a new Client configured with profile data from configuration files.

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
            backend_type (schemas.BackendType, optional): Which mode to use. Defaults to deployed.
                In deployed mode, assets are registered on a deployed platform which also executes the tasks.
                In local mode (subprocess or docker), if no URL is given then all assets are created locally and tasks
                are executed locally.
                In local mode (subprocess or docker), if a URL is given then the mode is a hybrid one: new assets are
                created locally but can access assets from the deployed Substra platform. The platform is in read-only
                mode and tasks are executed locally.
                The local mode is either docker or subprocess mode: `docker` if you want the tasks to
                be executed in containers (default) or `subprocess` to execute them in Python subprocesses (faster,
                experimental: The `Dockerfile` commands are not executed, requires dependencies to be installed
                locally).

        Returns:
            Client: The new client.
        """

        config_path = os.path.expanduser(config_path)
        profile = cfg.ConfigManager(config_path).get_profile(profile_name)
        if not token:
            try:
                tokens_path = os.path.expanduser(tokens_path)
                token = cfg.TokenManager(tokens_path).get_profile(profile_name)
            except cfg.ProfileNotFoundError:
                token = None
        return Client(
            token=token,
            retry_timeout=retry_timeout,
            url=profile["url"],
            insecure=profile["insecure"],
            backend_type=backend_type,
        )

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
    def add_algo(self, data: Union[dict, schemas.AlgoSpec]) -> str:
        """Create new algo asset.

        Args:
            data (Union[dict, schemas.AlgoSpec]): If it is a dict, it must have the same keys
                as specified in [schemas.AlgoSpec](sdk_schemas.md#AlgoSpec).

        Returns:
            str: Key of the algo
        """
        spec = self._get_spec(schemas.AlgoSpec, data)
        return self._backend.add(spec)

    @logit
    def add_traintuple(self, data: Union[dict, schemas.TraintupleSpec]) -> str:
        """Create new traintuple asset.

        Args:
            data (Union[dict, schemas.TraintupleSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.TraintupleSpec](sdk_schemas.md#TraintupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.TraintupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_aggregatetuple(self, data: Union[dict, schemas.AggregatetupleSpec]) -> str:
        """Create a new aggregate tuple asset.

        Args:
            data (Union[dict, schemas.AggregatetupleSpec]): If it is a dict, it must have the same
                keys as specified in
                [schemas.AggregatetupleSpec](sdk_schemas.md#AggregatetupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.AggregatetupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_composite_traintuple(self, data: Union[dict, schemas.CompositeTraintupleSpec]) -> str:
        """Create new composite traintuple asset.

        As specified in the data structure, output trunk models cannot be made
        public.

        Args:
            data (Union[dict, schemas.CompositeTraintupleSpec]): If it is a dict, it must have the
                same keys as specified in
                [schemas.CompositeTraintupleSpec](sdk_schemas.md#CompositeTraintupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.CompositeTraintupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_predicttuple(self, data: Union[dict, schemas.PredicttupleSpec]) -> str:
        """Create new predicttuple asset.

        Args:
            data (Union[dict, schemas.PredicttupleSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.PredicttupleSpec](sdk_schemas.md#PredicttupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.PredicttupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_testtuple(self, data: Union[dict, schemas.TesttupleSpec]) -> str:
        """Create new testtuple asset.

        Args:
            data (Union[dict, schemas.TesttupleSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.TesttupleSpec](sdk_schemas.md#TesttupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.TesttupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_compute_plan(
        self,
        data: Union[dict, schemas.ComputePlanSpec],
        auto_batching: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> models.ComputePlan:
        """Create new compute plan asset.

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.

        Args:
            data (Union[dict, schemas.ComputePlanSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.ComputePlanSpec](sdk_schemas.md#ComputePlanSpec).
            auto_batching (bool, optional): Set 'auto_batching' to False to upload all the tuples of
                the compute plan at once. Defaults to True.
            batch_size (int, optional): If 'auto_batching' is True, change `batch_size` to define
                the number of tuples uploaded in each batch (default 500).

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
    def get_algo(self, key: str) -> models.Algo:
        """Get algo by key, the returned object is described
        in the [models.Algo](sdk_models.md#Algo) model"""
        return self._backend.get(schemas.Type.Algo, key)

    @logit
    def get_compute_plan(self, key: str) -> models.ComputePlan:
        """Get compute plan by key, the returned object is described
        in the [models.ComputePlan](sdk_models.md#ComputePlan) model"""
        return self._backend.get(schemas.Type.ComputePlan, key)

    @logit
    def get_performances(self, key: str) -> models.Performances:
        """Get the compute plan performances by key, the returned object is described
        in the [models.Performances](sdk_models.md#Performances) and easily convertible
        to pandas dataframe.

        Example:
            ```python
            perf = client.get_performances(cp_key)
            df = pd.DataFrame(perf.dict())
            print(df)
            ```
        """

        performances = self._backend.get_performances(key)

        return performances

    @logit
    def get_dataset(self, key: str) -> models.Dataset:
        """Get dataset by key, the returned object is described
        in the [models.Dataset](sdk_models.md#Dataset) model"""
        return self._backend.get(schemas.Type.Dataset, key)

    @logit
    def get_predicttuple(self, key: str) -> models.Predicttuple:
        """Get predicttuple by key, the returned object is described
        in the [models.Predicttuple](sdk_models.md#Predicttuple) model"""
        return self._backend.get(schemas.Type.Predicttuple, key)

    @logit
    def get_testtuple(self, key: str) -> models.Testtuple:
        """Get testtuple by key, the returned object is described
        in the [models.Testtuple](sdk_models.md#Testtuple) model"""
        return self._backend.get(schemas.Type.Testtuple, key)

    @logit
    def get_traintuple(self, key: str) -> models.Traintuple:
        """Get traintuple by key, the returned object is described
        in the [models.Traintuple](sdk_models.md#Traintuple) model"""
        return self._backend.get(schemas.Type.Traintuple, key)

    @logit
    def get_aggregatetuple(self, key: str) -> models.Aggregatetuple:
        """Get aggregatetuple by key, the returned object is described
        in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model"""
        return self._backend.get(schemas.Type.Aggregatetuple, key)

    @logit
    def get_composite_traintuple(self, key: str) -> models.CompositeTraintuple:
        """Get composite traintuple by key, the returned object is described
        in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model"""
        return self._backend.get(schemas.Type.CompositeTraintuple, key)

    @logit
    def get_logs(self, tuple_key: str) -> str:
        """Get tuple logs by tuple key, the returned object is a string
        containing the logs.

        Logs are only available for tuples that experienced an execution failure.
        Attempting to retrieve logs for tuples in any other states or for non-existing
        tuples will result in a NotFound error.
        """
        return self._backend.download_logs(tuple_key, destination_file=None)

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
    def list_algo(self, filters: dict = None, ascending: bool = False) -> List[models.Algo]:
        """List algos.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list algo with given keys.\n
            name (str): list algo with name partially matching given string. Remote mode only.\n
            owner (List[str]): list algo with given owners.\n
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list algo matching provided conditions in metadata.\n
            permissions (List[str]): list algo which can be used by any of the listed nodes. Remote mode only.
            compute_plan_key (str): list algo that are in the given compute plan. Remote mode only.
            dataset_key (str): list algo linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list algo linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            ascending (bool, optional): Sorts results by oldest creation_date first. Default False (descending order).

        Returns:
            models.Algo: the returned object is described in the [models.Algo](sdk_models.md#Algo) model

        """

        return self._list(schemas.Type.Algo, filters, "creation_date", ascending)

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
            algo_key (str): list compute plans that used the given algo. Remote mode only.
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
                algo_key (str): list data samples that used the given algo. Remote mode only.
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
            algo_key (str): list dataset that used the given algo. Remote mode only.
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
    def list_predicttuple(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.Predicttuple]:
        """List predicttuples.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list predicttuples with listed keys.\n
            owner (List[str]): list predicttuples with listed owners.\n
            worker (List[str]): list predicttuples which ran on listed workers. Remote mode only.\n
            rank (List[int]): list predicttuples which are at given ranks.\n
            status (List[str]): list predicttuples with given status.
                The possible values are the values of `substra.models.Status`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list predicttuples matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list predicttuples that are in the given compute plan. Remote mode only.
            algo_key (str): list predicttuples that used the given algo. Remote mode only.
            dataset_key (str): list predicttuples linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list predicttuples linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.Predicttuple: the returned object is described in the
                [models.Predicttuple](sdk_models.md#Predicttuple) model


        """

        return self._list(schemas.Type.Predicttuple, filters, order_by, ascending)

    @logit
    def list_testtuple(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.Testtuple]:
        """List testtuples.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list testtuples with listed keys.\n
            owner (List[str]): list testtuples with listed owners.\n
            worker (List[str]): list testtuples which ran on listed workers. Remote mode only.\n
            rank (List[int]): list testtuples which are at given ranks.\n
            status (List[str]): list testtuples with given status.
                The possible values are the values of `substra.models.Status`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list testtuples matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list testtuples that are in the given compute plan. Remote mode only.
            algo_key (str): list testtuples that used the given algo. Remote mode only.
            dataset_key (str): list testtuples linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list testtuples linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.Testtuple: the returned object is described
        in the [models.Testtuple](sdk_models.md#Testtuple) model
        """

        return self._list(schemas.Type.Testtuple, filters, order_by, ascending)

    @logit
    def list_traintuple(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.Traintuple]:
        """List traintuples.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list traintuples with listed keys.\n
            owner (List[str]): list traintuples with listed owners.\n
            worker (List[str]): list traintuples which ran on listed workers. Remote mode only.\n
            rank (List[int]): list traintuples which are at given ranks.\n
            status (List[str]): list traintuples with given status.
                The possible values are the values of `substra.models.Status`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list traintuples matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list traintuples that are in the given compute plan. Remote mode only.
            algo_key (str): list traintuples that used the given algo. Remote mode only.
            dataset_key (str): list traintuples linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list traintuples linked or that used this data sample(s). Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.Traintuple: the returned object is described
        in the [models.Traintuple](sdk_models.md#Traintuple) model


        """

        return self._list(schemas.Type.Traintuple, filters, order_by, ascending)

    @logit
    def list_aggregatetuple(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.Aggregatetuple]:
        """List aggregatetuples.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list aggregatetuples with listed keys.\n
            owner (List[str]): list aggregatetuples with listed owners.\n
            worker (List[str]): list aggregatetuples which ran on listed workers. Remote mode only.\n
            rank (List[int]): list aggregatetuples which are at given ranks.\n
            status (List[str]): list aggregatetuples with given status.
                The possible values are the values of `substra.models.Status`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list aggregatetuples matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list aggregatetuples that are in the given compute plan. Remote mode only.
            algo_key (str): list aggregatetuples that used the given algo. Remote mode only.
            dataset_key (str): list aggregatetuples linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list aggregatetuples linked or that used this data sample(s). Remote mode only.


        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.Aggregatetuple: the returned object is described
        in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model
        """

        return self._list(schemas.Type.Aggregatetuple, filters, order_by, ascending)

    @logit
    def list_composite_traintuple(
        self, filters: dict = None, order_by: str = "creation_date", ascending: bool = False
    ) -> List[models.CompositeTraintuple]:
        """List composite traintuples.

        The ``filters`` argument is a dictionary, with those possible keys:\n
            key (List[str]): list composite traintuples with listed keys.\n
            owner (List[str]): list composite traintuples with listed owners.\n
            worker (List[str]): list composite traintuples which ran on listed workers. Remote mode only.\n
            rank (List[int]): list composite traintuples which are at given ranks.\n
            status (List[str]): list composite traintuples with given status.
                The possible values are the values of `substra.models.Status`
            metadata (dict)
                {
                    "key": str # the key of the metadata to filter on
                    "type": "is", "contains" or "exists" # the type of query that will be used
                    "value": str # the value that the key must be (if type is "is") or contain (if type if "contains")
                }: list composite traintuples matching provided conditions in metadata. Remote mode only.
            compute_plan_key (str): list composite traintuples that are in the given compute plan. Remote mode only.
            algo_key (str): list composite traintuples that used the given algo. Remote mode only.
            dataset_key (str): list composite traintuples linked or using this dataset. Remote mode only.
            data_sample_key (List[str]): list composite traintuples linked or that used this data sample(s).
                Remote mode only.

        Args:
            filters (dict, optional): List of key values pair to filter on. Default None.
            order_by (str, optional): Field to sort results by.
                Possible values: `creation_date`, `start_date`, `end_date`. Default creation_date.
            ascending (bool, optional): Sorts results on order_by by ascending order. Default False (descending order).

        Returns:
            models.CompositeTraintuple: the returned object is described
        in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model.


        """

        return self._list(schemas.Type.CompositeTraintuple, filters, order_by, ascending)

    @logit
    def list_organization(self, *args, **kwargs) -> List[models.Organization]:
        """List organizations, the returned object is described
        in the [models.Organization](sdk_models.md#Organization) model"""
        # results are not paginated for organizations
        return self._backend.list(schemas.Type.Organization, paginated=False)

    @logit
    def update_algo(self, key: str, name: str):
        spec = self._get_spec(schemas.UpdateAlgoSpec, {"name": name})
        self._backend.update(key, spec)
        return

    @logit
    def add_compute_plan_tuples(
        self,
        key: str,
        tuples: Union[dict, schemas.UpdateComputePlanTuplesSpec],
        auto_batching: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> models.ComputePlan:
        """Update compute plan.

        As specified in the tuples dict structure, output trunk models of composite
        traintuples cannot be made public.

        Args:
            key (str): Compute plan key
            tuples (Union[dict, schemas.UpdateComputePlanTuplesSpec]): If it is a dict,
                it must have the same keys as specified in
                [schemas.UpdateComputePlanTuplesSpec](sdk_schemas.md#UpdateComputePlanTuplesSpec).
            auto_batching (bool, optional): Set 'auto_batching' to False to upload all
                the tuples of the compute plan at once. Defaults to True.
            batch_size (int, optional): If 'auto_batching' is True, change `batch_size`
                to define the number of tuples uploaded in each batch (default 500).

        Returns:
            models.ComputePlan: updated compute plan, as described in the
            [models.ComputePlan](sdk_models.md#ComputePlan) model
        """
        if isinstance(tuples, dict):
            tuples["key"] = key
        spec = self._get_spec(schemas.UpdateComputePlanTuplesSpec, tuples)
        spec_options = {
            "auto_batching": auto_batching,
            "batch_size": batch_size,
        }
        return self._backend.add_compute_plan_tuples(spec, spec_options=spec_options)

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
        data_sample_keys: str,
    ) -> List[str]:
        """Link dataset with data samples."""
        return self._backend.link_dataset_with_data_samples(dataset_key, data_sample_keys)

    @logit
    def download_dataset(self, key: str, destination_folder: str) -> None:
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
    def download_algo(self, key: str, destination_folder: str) -> None:
        """Download algo resource.
        Download algo package in destination folder.

        Args:
            key (str): Algo key to download
            destination_folder (str): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded algo
        """

        return pathlib.Path(
            self._backend.download(
                schemas.Type.Algo,
                "algorithm.storage_address",
                key,
                os.path.join(destination_folder, "algo.tar.gz"),
            )
        )

    @logit
    def download_model(self, key: str, destination_folder) -> None:
        """Download model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.

        Args:
            key (str): Model key to download
            destination_folder (str): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """

        return pathlib.Path(self._backend.download_model(key, os.path.join(destination_folder, f"model_{key}")))

    @logit
    def download_model_from_traintuple(self, tuple_key: str, folder) -> None:
        """Download traintuple model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.

        Args:
            tuple_key (str): Tuple key to download
            folder (_type_): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """

        return pathlib.Path(self._download_model_from_tuple(schemas.Type.Traintuple, tuple_key, folder))

    @logit
    def download_model_from_aggregatetuple(self, tuple_key: str, folder) -> None:
        """Download aggregatetuple model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.

        Args:
            tuple_key (str): Tuple key to download
            folder (_type_): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """
        return pathlib.Path(self._download_model_from_tuple(schemas.Type.Aggregatetuple, tuple_key, folder))

    @logit
    def download_head_model_from_composite_traintuple(self, tuple_key: str, folder) -> None:
        """Download composite traintuple head model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.

        Args:
            tuple_key (str): Tuple key to download
            folder (_type_): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """
        return pathlib.Path(
            self._download_model_from_tuple(schemas.Type.CompositeTraintuple, tuple_key, folder, "head")
        )

    @logit
    def download_trunk_model_from_composite_traintuple(self, tuple_key: str, folder) -> None:
        """Download composite traintuple trunk model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.

        Args:
            tuple_key (str): Tuple key to download
            folder (_type_): Destination folder

        Returns:
            pathlib.Path: Path of the downloaded model
        """
        return pathlib.Path(
            self._download_model_from_tuple(schemas.Type.CompositeTraintuple, tuple_key, folder, "trunk")
        )

    def _download_model_from_tuple(self, tuple_type, tuple_key, folder, head_trunk=None) -> None:
        """Download model to a destination file."""
        tuple = self._backend.get(tuple_type, tuple_key)
        model = None
        if tuple_type == schemas.Type.CompositeTraintuple:
            identifier = HEAD_OUTPUT_IDENTIFIER if head_trunk == "head" else TRUNK_OUTPUT_IDENTIFIER
            model = tuple.outputs[identifier].value
        elif tuple_type == schemas.Type.Aggregatetuple:
            model = tuple.outputs[MODEL_OUTPUT_IDENTIFIER].value
        elif tuple_type == schemas.Type.Traintuple:
            model = tuple.outputs[MODEL_OUTPUT_IDENTIFIER].value
        else:
            raise exceptions.InvalidRequest(f"unhandled tuple type: {tuple_type}")

        if not model:
            desc = f"{head_trunk} " if head_trunk else ""
            msg = f'{tuple_type} {tuple_key}, status "{tuple.status}" has no {desc}out-model'
            raise exceptions.NotFound(msg, 404)

        return self.download_model(model.key, folder)

    @logit
    def download_logs(self, tuple_key: str, folder: str) -> str:
        """Download the execution logs of a failed tuple to a destination file.

        The logs are saved in the folder to a file named 'tuple_logs_{tuple_key}.txt'.

        Logs are only available for tuples that experienced an execution failure.
        Attempting to retrieve logs for tuples in any other states or for non-existing
        tuples will result in a NotFound error.

        Args:
            tuple_key: the key of the tuple that produced the logs
            folder: the destination directory

        Returns:
            str: The logs as a str
        """
        return self._backend.download_logs(tuple_key, os.path.join(folder, f"tuple_logs_{tuple_key}.txt"))

    @logit
    def describe_algo(self, key: str) -> str:
        """Get algo description."""
        return self._backend.describe(schemas.Type.Algo, key)

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
