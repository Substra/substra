# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import logging
import os
import pathlib
import time
from typing import Union, Optional, List

from substra.sdk import exceptions
from substra.sdk import config as cfg
from substra.sdk import backends
from substra.sdk import schemas, models

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60
DEFAULT_BATCH_SIZE = 20


def logit(f):
    """Decorator used to log all high-level methods of the Substra client."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug(f'{f.__name__}: call')
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
            logger.info(f'{f.__name__}: done in {elapsed:.2f}ms; error={error}')

    return wrapper


class Client(object):
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
        debug (bool, optional): Whether to use the default or debug mode.
            In debug mode, new assets are created locally but can access assets from
            the deployed Substra platform. The platform is in read-only mode.
            Defaults to False.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        retry_timeout: int = DEFAULT_RETRY_TIMEOUT,
        insecure: bool = False,
        debug: bool = False,
    ):
        self._retry_timeout = retry_timeout
        self._token = token

        self._insecure = insecure
        self._url = url

        self._backend = self._get_backend(debug)

    def _get_backend(self, debug: bool):
        # Three possibilities:
        # - debug is False: get a remote backend
        # - debug is True and no url is defined: fully local backend
        # - debug is True and url is defined: local backend that connects to
        #                           a remote backend (read-only)
        backend = None
        if (debug and self._url) or not debug:
            backend = backends.get(
                "remote",
                url=self._url,
                insecure=self._insecure,
                token=self._token,
                retry_timeout=self._retry_timeout,
            )
        if debug:
            # Hybrid mode: the local backend also connects to
            # a remote backend in read-only mode.
            return backends.get(
                "local",
                backend,
            )
        return backend

    @property
    def temp_directory(self):
        """Temporary directory for storing assets in debug mode.
        Deleted when the client is deleted.
        """
        if isinstance(self._backend, backends.Local):
            return self._backend.temp_directory

    @logit
    def login(self, username, password):
        """Login to a remote server. """
        if not self._backend:
            raise exceptions.SDKException('No backend found')
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
        debug: bool = False
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
            debug (bool): Whether to use the default or debug mode. In debug mode, new assets are
                created locally but can get remote assets. The deployed platform is in
                read-only mode.
                Defaults to False.

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
            url=profile['url'],
            insecure=profile['insecure'],
            debug=debug,
        )

    @logit
    def add_data_sample(
        self,
        data: Union[dict, schemas.DataSampleSpec],
        local: bool = True
    ) -> str:
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
        return self._backend.add(
            spec,
            spec_options=spec_options
        )

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

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the node owner of the data, and all tuples using this data
        have their worker set to this node. This has no impact on how the tuples are
        executed except if chainkey support is enabled.

        Args:
            data (Union[dict, schemas.DatasetSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.DatasetSpec](sdk_schemas.md#DatasetSpec).

        Returns:
            str: Key of the dataset
        """
        spec = self._get_spec(schemas.DatasetSpec, data)
        return self._backend.add(spec)

    @logit
    def add_objective(
        self,
        data: Union[dict, schemas.ObjectiveSpec],
    ) -> str:
        """Create new objective asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the objective.

        Args:
            data (Union[dict, schemas.ObjectiveSpec]): If it is a dict, it must have the same keys
                as specified in [schemas.ObjectiveSpec](sdk_schemas.md#ObjectiveSpec).

        Returns:
            str: Key of the objective
        """
        spec = self._get_spec(schemas.ObjectiveSpec, data)
        return self._backend.add(spec)

    @logit
    def add_algo(self, data: Union[dict, schemas.AlgoSpec]) -> str:
        """Create new algo asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the algo.

        Args:
            data (Union[dict, schemas.AlgoSpec]): If it is a dict, it must have the same keys
                as specified in [schemas.AlgoSpec](sdk_schemas.md#AlgoSpec).

        Returns:
            str: Key of the algo
        """
        spec = self._get_spec(schemas.AlgoSpec, data)
        return self._backend.add(spec)

    @logit
    def add_aggregate_algo(
        self,
        data: Union[dict, schemas.AggregateAlgoSpec],
    ) -> str:
        """Create new aggregate algo asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the aggregate algo.

        Args:
            data (Union[dict, schemas.AggregateAlgoSpec]): If it is a dict,
                it must have the same keys as specified in
                [schemas.AggregateAlgoSpec](sdk_schemas.md#AggregateAlgoSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.AggregateAlgoSpec, data)
        return self._backend.add(spec)

    @logit
    def add_composite_algo(
        self,
        data: Union[dict, schemas.CompositeAlgoSpec]
    ) -> str:
        """Create new composite algo asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the composite algo.

        Args:
            data (Union[dict, schemas.CompositeAlgoSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.CompositeAlgoSpec](sdk_schemas.md#CompositeAlgoSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.CompositeAlgoSpec, data)
        return self._backend.add(spec)

    @logit
    def add_traintuple(
        self,
        data: Union[dict, schemas.TraintupleSpec]
    ) -> str:
        """Create new traintuple asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the traintuple.

        Args:
            data (Union[dict, schemas.TraintupleSpec]): If it is a dict, it must have the same
                keys as specified in [schemas.TraintupleSpec](sdk_schemas.md#TraintupleSpec).

        Returns:
            str: Key of the asset
        """
        spec = self._get_spec(schemas.TraintupleSpec, data)
        return self._backend.add(spec)

    @logit
    def add_aggregatetuple(
        self,
        data: Union[dict, schemas.AggregatetupleSpec]
    ) -> str:
        """Create a new aggregate tuple asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the aggregate tuple.

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
    def add_composite_traintuple(
        self,
        data: Union[dict, schemas.CompositeTraintupleSpec]
    ) -> str:
        """Create new composite traintuple asset.

        As specified in the data structure, output trunk models cannot be made
        public.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the composite traintuple.

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
    def add_testtuple(
        self,
        data: Union[dict, schemas.TesttupleSpec]
    ) -> str:
        """Create new testtuple asset.

        In debug mode, add the following key: `substra.DEBUG_OWNER` to the metadata,
        the value becomes the 'creator' of the testtuple.

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
                the number of tuples uploaded in each batch (default 20).

        Returns:
            models.ComputePlan: Created compute plan
        """
        spec = self._get_spec(schemas.ComputePlanSpec, data)
        spec_options = {
            "auto_batching": auto_batching,
            "batch_size": batch_size,
        }
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
    def get_aggregate_algo(self, key: str) -> models.AggregateAlgo:
        """Get aggregate algo by key, the returned object is described
        in the [models.AggregateAlgo](sdk_models.md#AggregateAlgo) model"""
        return self._backend.get(schemas.Type.AggregateAlgo, key)

    @logit
    def get_composite_algo(self, key: str) -> models.CompositeAlgo:
        """Get composite algo by key, the returned object is described
        in the [models.CompositeAlgo](sdk_models.md#CompositeAlgo) model"""
        return self._backend.get(schemas.Type.CompositeAlgo, key)

    @logit
    def get_dataset(self, key: str) -> models.Dataset:
        """Get dataset by key, the returned object is described
        in the [models.Dataset](sdk_models.md#Dataset) model"""
        return self._backend.get(schemas.Type.Dataset, key)

    @logit
    def get_objective(self, key: str) -> models.Objective:
        """Get objective by key, the returned object is described
        in the [models.Objective](sdk_models.md#Objective) model"""
        return self._backend.get(schemas.Type.Objective, key)

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
    def list_algo(self, filters=None) -> List[models.Algo]:
        """List algos, the returned object is described
        in the [models.Algo](sdk_models.md#Algo) model"""
        return self._backend.list(schemas.Type.Algo, filters)

    @logit
    def list_compute_plan(self, filters=None) -> List[models.ComputePlan]:
        """List compute plans, the returned object is described
        in the [models.ComputePlan](sdk_models.md#ComputePlan) model"""
        return self._backend.list(schemas.Type.ComputePlan, filters)

    @logit
    def list_aggregate_algo(self, filters=None) -> List[models.AggregateAlgo]:
        """List aggregate algos, the returned object is described
        in the [models.AggregateAlgo](sdk_models.md#AggregateAlgo) model"""
        return self._backend.list(schemas.Type.AggregateAlgo, filters)

    @logit
    def list_composite_algo(self, filters=None) -> List[models.CompositeAlgo]:
        """List composite algos, the returned object is described
        in the [models.CompositeAlgo](sdk_models.md#CompositeAlgo) model"""
        return self._backend.list(schemas.Type.CompositeAlgo, filters)

    @logit
    def list_data_sample(self, filters=None) -> List[models.DataSample]:
        """List data samples, the returned object is described
        in the [models.DataSample](sdk_models.md#DataSample) model"""
        return self._backend.list(schemas.Type.DataSample, filters)

    @logit
    def list_dataset(self, filters=None) -> List[models.Dataset]:
        """List datasets, the returned object is described
        in the [models.Dataset](sdk_models.md#Dataset) model"""
        return self._backend.list(schemas.Type.Dataset, filters)

    @logit
    def list_objective(self, filters=None) -> List[models.Objective]:
        """List objectives, the returned object is described
        in the [models.Objective](sdk_models.md#Objective) model"""
        return self._backend.list(schemas.Type.Objective, filters)

    @logit
    def list_testtuple(self, filters=None) -> List[models.Testtuple]:
        """List testtuples, the returned object is described
        in the [models.Testtuple](sdk_models.md#Testtuple) model"""
        return self._backend.list(schemas.Type.Testtuple, filters)

    @logit
    def list_traintuple(self, filters=None) -> List[models.Traintuple]:
        """List traintuples, the returned object is described
        in the [models.Traintuple](sdk_models.md#Traintuple) model"""
        return self._backend.list(schemas.Type.Traintuple, filters)

    @logit
    def list_aggregatetuple(self, filters=None) -> List[models.Aggregatetuple]:
        """List aggregatetuples, the returned object is described
        in the [models.Aggregatetuple](sdk_models.md#Aggregatetuple) model"""
        return self._backend.list(schemas.Type.Aggregatetuple, filters)

    @logit
    def list_composite_traintuple(self, filters=None) -> List[models.CompositeTraintuple]:
        """List composite traintuples, the returned object is described
        in the [models.CompositeTraintuple](sdk_models.md#CompositeTraintuple) model"""
        return self._backend.list(schemas.Type.CompositeTraintuple, filters)

    @logit
    def list_node(self, *args, **kwargs) -> List[models.Node]:
        """List nodes, the returned object is described
        in the [models.Node](sdk_models.md#Node) model"""
        return self._backend.list(schemas.Type.Node)

    @logit
    def update_compute_plan(
        self,
        key: str,
        data: Union[dict, schemas.UpdateComputePlanSpec],
        auto_batching: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE
    ) -> models.ComputePlan:
        """Update compute plan.

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.

        Args:
            key (str): Compute plan key
            data (Union[dict, schemas.UpdateComputePlanSpec]): If it is a dict,
                it must have the same keys as specified in
                [schemas.UpdateComputePlanSpec](sdk_schemas.md#UpdateComputePlanSpec).
            auto_batching (bool, optional): Set 'auto_batching' to False to upload all
                the tuples of the compute plan at once. Defaults to True.
            batch_size (int, optional): If 'auto_batching' is True, change `batch_size`
                to define the number of tuples uploaded in each batch (default 20).

        Returns:
            models.ComputePlan: updated compute plan, as described in the
            [models.ComputePlan](sdk_models.md#ComputePlan) model
        """
        spec = self._get_spec(schemas.UpdateComputePlanSpec, data)
        spec_options = {
            "auto_batching": auto_batching,
            "batch_size": batch_size,
        }
        return self._backend.update_compute_plan(
            key,
            spec,
            spec_options=spec_options
        )

    @logit
    def link_dataset_with_objective(self, dataset_key: str, objective_key: str) -> str:
        """Link dataset with objective."""
        return self._backend.link_dataset_with_objective(dataset_key, objective_key)

    @logit
    def link_dataset_with_data_samples(
        self, dataset_key: str,
        data_sample_keys: str,
    ) -> List[str]:
        """Link dataset with data samples."""
        return self._backend.link_dataset_with_data_samples(
            dataset_key, data_sample_keys
        )

    @logit
    def download_dataset(self, key: str, destination_folder: str) -> None:
        """Download data manager resource.

        Download opener script in destination folder.
        """
        self._backend.download(
            schemas.Type.Dataset,
            'opener.storage_address',
            key,
            os.path.join(destination_folder, 'opener.py'),
        )

    @logit
    def download_algo(self, key: str, destination_folder: str) -> None:
        """Download algo resource.

        Download algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.Algo,
            'content.storage_address',
            key,
            os.path.join(destination_folder, 'algo.tar.gz'),
        )

    @logit
    def download_aggregate_algo(self, key: str, destination_folder: str) -> None:
        """Download aggregate algo resource.

        Download aggregate algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.AggregateAlgo,
            'content.storage_address',
            key,
            os.path.join(destination_folder, 'aggregate_algo.tar.gz'),
        )

    @logit
    def download_composite_algo(self, key: str, destination_folder: str) -> None:
        """Download composite algo resource.

        Download composite algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.CompositeAlgo,
            'content.storage_address',
            key,
            os.path.join(destination_folder, 'composite_algo.tar.gz'),
        )

    @logit
    def download_objective(self, key: str, destination_folder: str) -> None:
        """Download objective resource.

        Download metrics script in destination folder.
        """
        self._backend.download(
            schemas.Type.Objective,
            'metrics.storage_address',
            key,
            os.path.join(destination_folder, 'metrics.py'),
        )

    @logit
    def download_model(self, key: str, folder) -> None:
        """Download model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.
        """
        self._backend.download_model(key, os.path.join(folder, f'model_{key}'))

    @logit
    def download_model_from_traintuple(self, tuple_key: str, folder) -> None:
        """Download traintuple model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.
        """
        self._download_model_from_tuple(schemas.Type.Traintuple, tuple_key, folder)

    @logit
    def download_model_from_aggregatetuple(self, tuple_key: str, folder) -> None:
        """Download aggregatetuple model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.
        """
        self._download_model_from_tuple(schemas.Type.Aggregatetuple, tuple_key, folder)

    @logit
    def download_head_model_from_composite_traintuple(self, tuple_key: str, folder) -> None:
        """Download composite traintuple head model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.
        """
        self._download_model_from_tuple(schemas.Type.CompositeTraintuple, tuple_key, folder, "head")

    @logit
    def download_trunk_model_from_composite_traintuple(self, tuple_key: str, folder) -> None:
        """Download composite traintuple trunk model to destination file.

        This model was saved using the 'save_model' function of the algorithm.
        To load and use the model, please refer to the 'load_model' and 'predict' functions of the
        algorithm.
        """
        self._download_model_from_tuple(schemas.Type.CompositeTraintuple, tuple_key, folder,
                                        "trunk")

    def _download_model_from_tuple(self, tuple_type, tuple_key, folder, head_trunk=None) -> None:
        """Download model to a destination file."""
        tuple = self._backend.get(tuple_type, tuple_key)

        if tuple_type == schemas.Type.CompositeTraintuple:
            if head_trunk == "head":
                model = tuple.out_head_model.out_model
            elif head_trunk == "trunk":
                model = tuple.out_trunk_model.out_model
            else:
                raise exceptions.InvalidRequest(
                    'head_trunk parameter must have value "head" or "trunk"'
                )
        else:
            model = tuple.out_model

        if not model:
            desc = f'{head_trunk} ' if head_trunk else ""
            msg = f'{tuple_type} {tuple_key}, status "{tuple.status}" has no {desc}out-model'
            raise exceptions.NotFound(msg, 404)

        self.download_model(model.key, folder)

    @logit
    def describe_algo(self, key: str) -> str:
        """Get algo description."""
        return self._backend.describe(schemas.Type.Algo, key)

    @logit
    def describe_aggregate_algo(self, key: str) -> str:
        """Get aggregate algo description."""
        return self._backend.describe(schemas.Type.AggregateAlgo, key)

    @logit
    def describe_composite_algo(self, key: str) -> str:
        """Get composite algo description."""
        return self._backend.describe(schemas.Type.CompositeAlgo, key)

    @logit
    def describe_dataset(self, key: str) -> str:
        """Get dataset description."""
        return self._backend.describe(schemas.Type.Dataset, key)

    @logit
    def describe_objective(self, key: str) -> str:
        """Get objective description."""
        return self._backend.describe(schemas.Type.Objective, key)

    @logit
    def node_info(self) -> str:
        """Get node information."""
        return self._backend.node_info()

    @logit
    def leaderboard(self, objective_key: str, sort: str = 'desc') -> str:
        """Get objective leaderboard"""
        return self._backend.leaderboard(objective_key, sort='desc')

    @logit
    def cancel_compute_plan(self, key: str) -> models.ComputePlan:
        """Cancel execution of compute plan, the returned object is described
        in the [models.ComputePlan](sdk_models.md#ComputePlan) model"""
        return self._backend.cancel_compute_plan(key)
