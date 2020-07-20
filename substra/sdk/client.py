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
import typing

from substra.sdk import exceptions
from substra.sdk import config as cfg
from substra.sdk import user
from substra.sdk import backends
from substra.sdk import schemas

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60


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
            elaps = (te - ts) * 1000
            logger.info(f'{f.__name__}: done in {elaps:.2f}ms; error={error}')

    return wrapper


def _load_token_from_file(path=None):
    manager = user.Manager(path or user.DEFAULT_PATH)
    try:
        creds = manager.load_user()
    except (exceptions.UserException, FileNotFoundError):
        return None
    return creds.get('token')


class Client(object):
    """Create the client.

    Set the `backend` to 'local' to use the local debugging.
    One client corresponds to one profile.
    """

    def __init__(
        self,
        url: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        retry_timeout: int = DEFAULT_RETRY_TIMEOUT,
        backend: str = 'remote',
        version: str = '0.0',
        insecure: bool = False,
    ):
        self._backend_name = backend
        self._retry_timeout = retry_timeout
        self._token = token

        self._insecure = insecure
        self._url = url
        self._version = version

        self._backend = self._get_backend()

    def _get_backend(self):
        return backends.get(
            self._backend_name,
            url=self._url,
            version=self._version,
            insecure=self._insecure,
            token=self._token,
            retry_timeout=self._retry_timeout,
        )

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
        profile_name: typing.Optional[str] = None,
        config_path: typing.Union[str, pathlib.Path, None] = None,
        user_path: typing.Union[str, pathlib.Path, None] = None,
        token: typing.Optional[str] = None,
        retry_timeout: int = DEFAULT_RETRY_TIMEOUT,
        backend: str = 'remote',
    ):
        cfg_manager = cfg.Manager(config_path)
        profile = cfg_manager.from_config_file(name=profile_name)
        if not token:
            token = _load_token_from_file(user_path)
        return Client(
            token=token,
            retry_timeout=retry_timeout,
            backend=backend,
            url=profile['url'],
            version=profile['version'],
            insecure=profile['insecure'],
        )

    @logit
    def add_data_sample(self, data, local=True, exist_ok=False):
        """Create new data sample asset.

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

        """
        spec = self._get_spec(schemas.DataSampleSpec, data)
        if spec.paths:
            raise ValueError("data: invalid 'paths' field")
        if not spec.path:
            raise ValueError("data: missing 'path' field")
        spec_options = {
            "local": local,
        }
        return self._backend.add(spec, exist_ok=exist_ok, spec_options=spec_options)

    @logit
    def add_data_samples(self, data, local=True):
        """Create many data sample assets.

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
        """
        spec = self._get_spec(schemas.DataSampleSpec, data)
        if spec.path:
            raise ValueError("data: invalid 'path' field")
        if not spec.paths:
            raise ValueError("data: missing 'paths' field")
        spec_options = {
            "local": local,
        }
        return self._backend.add(spec, exist_ok=False, spec_options=spec_options)

    @logit
    def add_dataset(self, data, exist_ok=False):
        """Create new dataset asset.

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
        """
        spec = self._get_spec(schemas.DatasetSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_objective(self, data, exist_ok=False):
        """Create new objective asset.

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
        """
        spec = self._get_spec(schemas.ObjectiveSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_algo(self, data, exist_ok=False):
        """Create new algo asset.

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
        """
        spec = self._get_spec(schemas.AlgoSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_aggregate_algo(self, data, exist_ok=False):
        """Create new aggregate algo asset.
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
        """
        spec = self._get_spec(schemas.AggregateAlgoSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_composite_algo(self, data, exist_ok=False):
        """Create new composite algo asset.
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
        """
        spec = self._get_spec(schemas.CompositeAlgoSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_traintuple(self, data, exist_ok=False):
        """Create new traintuple asset.

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
        """
        spec = self._get_spec(schemas.TraintupleSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_aggregatetuple(self, data, exist_ok=False):
        """Create new aggregatetuple asset.
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
        """
        spec = self._get_spec(schemas.AggregatetupleSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_composite_traintuple(self, data, exist_ok=False):
        """Create new composite traintuple asset.
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
        """
        spec = self._get_spec(schemas.CompositeTraintupleSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_testtuple(self, data, exist_ok=False):
        """Create new testtuple asset.

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
        """
        spec = self._get_spec(schemas.TesttupleSpec, data)
        return self._backend.add(spec, exist_ok=exist_ok)

    @logit
    def add_compute_plan(self, data):
        """Create compute plan.

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
        """
        spec = self._get_spec(schemas.ComputePlanSpec, data)
        return self._backend.add(spec, exist_ok=False)

    @logit
    def get_algo(self, key):
        """Get algo by key."""
        return self._backend.get(schemas.Type.Algo, key)

    @logit
    def get_compute_plan(self, key):
        """Get compute plan by key."""
        return self._backend.get(schemas.Type.ComputePlan, key)

    @logit
    def get_aggregate_algo(self, key):
        """Get aggregate algo by key."""
        return self._backend.get(schemas.Type.AggregateAlgo, key)

    @logit
    def get_composite_algo(self, key):
        """Get composite algo by key."""
        return self._backend.get(schemas.Type.CompositeAlgo, key)

    @logit
    def get_dataset(self, key):
        """Get dataset by key."""
        return self._backend.get(schemas.Type.Dataset, key)

    @logit
    def get_objective(self, key):
        """Get objective by key."""
        return self._backend.get(schemas.Type.Objective, key)

    @logit
    def get_testtuple(self, key):
        """Get testtuple by key."""
        return self._backend.get(schemas.Type.Testtuple, key)

    @logit
    def get_traintuple(self, key):
        """Get traintuple by key."""
        return self._backend.get(schemas.Type.Traintuple, key)

    @logit
    def get_aggregatetuple(self, key):
        """Get aggregatetuple by key."""
        return self._backend.get(schemas.Type.Aggregatetuple, key)

    @logit
    def get_composite_traintuple(self, key):
        """Get composite traintuple by key."""
        return self._backend.get(schemas.Type.CompositeTraintuple, key)

    @logit
    def list_algo(self, filters=None):
        """List algos."""
        return self._backend.list(schemas.Type.Algo, filters)

    @logit
    def list_compute_plan(self, filters=None):
        """List compute plans."""
        return self._backend.list(schemas.Type.ComputePlan, filters)

    @logit
    def list_aggregate_algo(self, filters=None):
        """List aggregate algos."""
        return self._backend.list(schemas.Type.AggregateAlgo, filters)

    @logit
    def list_composite_algo(self, filters=None):
        """List composite algos."""
        return self._backend.list(schemas.Type.CompositeAlgo, filters)

    @logit
    def list_data_sample(self, filters=None):
        """List data samples."""
        return self._backend.list(schemas.Type.DataSample, filters)

    @logit
    def list_dataset(self, filters=None):
        """List datasets."""
        return self._backend.list(schemas.Type.Dataset, filters)

    @logit
    def list_objective(self, filters=None):
        """List objectives."""
        return self._backend.list(schemas.Type.Objective, filters)

    @logit
    def list_testtuple(self, filters=None):
        """List testtuples."""
        return self._backend.list(schemas.Type.Testtuple, filters)

    @logit
    def list_traintuple(self, filters=None):
        """List traintuples."""
        return self._backend.list(schemas.Type.Traintuple, filters)

    @logit
    def list_aggregatetuple(self, filters=None):
        """List aggregatetuples."""
        return self._backend.list(schemas.Type.Aggregatetuple, filters)

    @logit
    def list_composite_traintuple(self, filters=None):
        """List composite traintuples."""
        return self._backend.list(schemas.Type.CompositeTraintuple, filters)

    @logit
    def list_node(self, *args, **kwargs):
        """List nodes."""
        return self._backend.list(schemas.Type.Node)

    @logit
    def update_compute_plan(self, compute_plan_id, data):
        """Update compute plan.

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

        """
        spec = schemas.UpdateComputePlanSpec(**data)
        return self._backend.update_compute_plan(compute_plan_id, spec)

    @logit
    def link_dataset_with_objective(self, dataset_key, objective_key):
        """Link dataset with objective."""
        return self._backend.link_dataset_with_objective(dataset_key, objective_key)

    @logit
    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        """Link dataset with data samples."""
        return self._backend.link_dataset_with_data_samples(
            dataset_key, data_sample_keys
        )

    @logit
    def download_dataset(self, key, destination_folder):
        """Download data manager resource.

        Download opener script in destination folder.
        """
        self._backend.download(
            schemas.Type.Dataset,
            'opener.storageAddress',
            key,
            os.path.join(destination_folder, 'opener.py'),
        )

    @logit
    def download_algo(self, key, destination_folder):
        """Download algo resource.

        Download algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.Algo,
            'content.storageAddress',
            key,
            os.path.join(destination_folder, 'algo.tar.gz'),
        )

    @logit
    def download_aggregate_algo(self, key, destination_folder):
        """Download aggregate algo resource.

        Download aggregate algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.AggregateAlgo,
            'content.storageAddress',
            key,
            os.path.join(destination_folder, 'aggregate_algo.tar.gz'),
        )

    @logit
    def download_composite_algo(self, key, destination_folder):
        """Download composite algo resource.

        Download composite algo package in destination folder.
        """
        self._backend.download(
            schemas.Type.CompositeAlgo,
            'content.storageAddress',
            key,
            os.path.join(destination_folder, 'composite_algo.tar.gz'),
        )

    @logit
    def download_objective(self, key, destination_folder):
        """Download objective resource.

        Download metrics script in destination folder.
        """
        self._backend.download(
            schemas.Type.Objective,
            'metrics.storageAddress',
            key,
            os.path.join(destination_folder, 'metrics.py'),
        )

    @logit
    def describe_algo(self, key):
        """Get algo description."""
        return self._backend.describe(schemas.Type.Algo, key)

    @logit
    def describe_aggregate_algo(self, key):
        """Get aggregate algo description."""
        return self._backend.describe(schemas.Type.AggregateAlgo, key)

    @logit
    def describe_composite_algo(self, key):
        """Get composite algo description."""
        return self._backend.describe(schemas.Type.CompositeAlgo, key)

    @logit
    def describe_dataset(self, key):
        """Get dataset description."""
        return self._backend.describe(schemas.Type.Dataset, key)

    @logit
    def describe_objective(self, key):
        """Get objective description."""
        return self._backend.describe(schemas.Type.Objective, key)

    @logit
    def leaderboard(self, objective_key, sort='desc'):
        """Get objective leaderboard"""
        return self._backend.leaderboard(objective_key, sort='desc')

    @logit
    def cancel_compute_plan(self, compute_plan_id):
        """Cancel execution of compute plan."""
        return self._backend.cancel_compute_plan(compute_plan_id)
