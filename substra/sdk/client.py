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
import time

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

    def __init__(self, config_path=None, profile_name=None, user_path=None,
                 token=None, retry_timeout=DEFAULT_RETRY_TIMEOUT, backend='remote'):
        # TODO deprecate add_profile method and update Client constructor (add a
        #      class constructor to init the Client from the config file or add a
        #      mismatch # method).
        self._backend_name = backend
        self._retry_timeout = retry_timeout
        self._token = token

        self._backend = None
        self._insecure = None
        self._url = None
        self._version = None

        if not self._token:
            self._token = _load_token_from_file(user_path)

        if not profile_name:
            return

    @logit
    def login(self, username, password):
        """Login.

        After setting your configuration with `substra config`, launch `substra login`.
        You will be prompted for your username and password and get a token which will be
        stored by default in `~/.substra-user`
        You can change that thanks to the --user option (works like the --profile option)
        """

        res = self.client.login(username, password)
        token = res.json()['token']
        self._set_token(token)
        return token

    def _set_token(self, token):
        if not self._current_profile:
            raise exceptions.SDKException("No profile defined")

        self._current_profile.update({
            'token': token,
        })
        self.client.set_config(self._current_profile, self._profile_name)
        return token

    def _set_current_profile(self, profile_name, profile):
        """Set client current profile."""
        self._profile_name = profile_name
        self._profiles[profile_name] = profile
        self._current_profile = profile
        self.client.set_config(self._current_profile, profile_name)

        self._backend_name = backend
        self._url = profile['url']
        self._version = profile['version']
        self._insecure = profile['insecure']

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

    def add_profile(self, profile_name, url, version='0.0', insecure=False):
        """Set client parameters."""
        self._url = url
        self._version = version
        self._insecure = insecure
        self._backend = self._get_backend()

    @logit
    def login(self, username, password):
        """Login to a remote server."""
        if not self._backend:
            raise exceptions.SDKException('No profile found')
        return self._backend.login(username, password)

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
        if 'paths' in data:
            raise ValueError("data: invalid 'paths' field")
        if 'path' not in data:
            raise ValueError("data: missing 'path' field")
        spec = schemas.DataSampleSpec(**data)
        spec_options = {
            'local': local,
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
        if 'path' in data:
            raise ValueError("data: invalid 'path' field")
        if 'paths' not in data:
            raise ValueError("data: missing 'paths' field")
        spec = schemas.DataSampleSpec(**data)
        spec_options = {
            'local': local,
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
        spec = schemas.DatasetSpec(**data)
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
        spec = schemas.ObjectiveSpec(**data)
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
        spec = schemas.AlgoSpec(**data)
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
        spec = schemas.AggregateAlgoSpec(**data)
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
        spec = schemas.CompositeAlgoSpec(**data)
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
        spec = schemas.TraintupleSpec(**data)
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
        spec = schemas.AggregatetupleSpec(**data)
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
        spec = schemas.CompositeTraintupleSpec(**data)
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
        spec = schemas.TesttupleSpec(**data)
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
        spec = schemas.ComputePlanSpec(**data)
        return self._backend.add(spec)

    @logit
    def get_algo(self, key):
        """Get algo by key."""
        return self._backend.get(schemas.AssetType.Algo, key)

    @logit
    def get_compute_plan(self, key):
        """Get compute plan by key."""
        return self._backend.get(schemas.AssetType.ComputePlan, key)

    @logit
    def get_aggregate_algo(self, key):
        """Get aggregate algo by key."""
        return self._backend.get(schemas.AssetType.AggregateAlgo, key)

    @logit
    def get_composite_algo(self, key):
        """Get composite algo by key."""
        return self._backend.get(schemas.AssetType.CompositeAlgo, key)

    @logit
    def get_dataset(self, key):
        """Get dataset by key."""
        return self._backend.get(schemas.AssetType.Dataset, key)

    @logit
    def get_objective(self, key):
        """Get objective by key."""
        return self._backend.get(schemas.AssetType.Objective, key)

    @logit
    def get_testtuple(self, key):
        """Get testtuple by key."""
        return self._backend.get(schemas.AssetType.Testtuple, key)

    @logit
    def get_traintuple(self, key):
        """Get traintuple by key."""
        return self._backend.get(schemas.AssetType.Traintuple, key)

    @logit
    def get_aggregatetuple(self, key):
        """Get aggregatetuple by key."""
        return self._backend.get(schemas.AssetType.Aggregatetuple, key)

    @logit
    def get_composite_traintuple(self, key):
        """Get composite traintuple by key."""
        return self._backend.get(schemas.AssetType.CompositeTraintuple, key)

    @logit
    def list_algo(self, filters=None):
        """List algos."""
        return self._backend.list(schemas.AssetType.Algo, filters)

    @logit
    def list_compute_plan(self, filters=None):
        """List compute plans."""
        return self._backend.list(schemas.AssetType.ComputePlan, filters)

    @logit
    def list_aggregate_algo(self, filters=None):
        """List aggregate algos."""
        return self._backend.list(schemas.AssetType.AggregateAlgo, filters)

    @logit
    def list_composite_algo(self, filters=None):
        """List composite algos."""
        return self._backend.list(schemas.AssetType.CompositeAlgo, filters)

    @logit
    def list_data_sample(self, filters=None):
        """List data samples."""
        return self._backend.list(schemas.AssetType.DataSample, filters)

    @logit
    def list_dataset(self, filters=None):
        """List datasets."""
        return self._backend.list(schemas.AssetType.Dataset, filters)

    @logit
    def list_objective(self, filters=None):
        """List objectives."""
        return self._backend.list(schemas.AssetType.Objective, filters)

    @logit
    def list_testtuple(self, filters=None):
        """List testtuples."""
        return self._backend.list(schemas.AssetType.Testtuple, filters)

    @logit
    def list_traintuple(self, filters=None):
        """List traintuples."""
        return self._backend.list(schemas.AssetType.Traintuple, filters)

    @logit
    def list_aggregatetuple(self, filters=None):
        """List aggregatetuples."""
        return self._backend.list(schemas.AssetType.Aggregatetuple, filters)

    @logit
    def list_composite_traintuple(self, filters=None):
        """List composite traintuples."""
        return self._backend.list(schemas.AssetType.CompositeTraintuple, filters)

    @logit
    def list_node(self, *args, **kwargs):
        """List nodes."""
        return self._backend.list(schemas.AssetType.Node)

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
        return self._backend.link_dataset_with_data_samples(dataset_key, data_sample_keys)

    @logit
    def download_dataset(self, key, destination_folder):
        """Download data manager resource.

        Download opener script in destination folder.
        """
        self._backend.download(
            schemas.AssetType.Dataset,
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
            schemas.AssetType.Algo,
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
            schemas.AssetType.AggregateAlgo,
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
            schemas.AssetType.CompositeAlgo,
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
            schemas.AssetType.Objective,
            'metrics.storageAddress',
            key,
            os.path.join(destination_folder, 'metrics.py'),
        )

    @logit
    def describe_algo(self, key):
        """Get algo description."""
        return self._backend.describe(schemas.AssetType.Algo, key)

    @logit
    def describe_aggregate_algo(self, key):
        """Get aggregate algo description."""
        return self._backend.describe(schemas.AssetType.AggregateAlgo, key)

    @logit
    def describe_composite_algo(self, key):
        """Get composite algo description."""
        return self._backend.describe(schemas.AssetType.CompositeAlgo, key)

    @logit
    def describe_dataset(self, key):
        """Get dataset description."""
        return self._backend.describe(schemas.AssetType.Dataset, key)

    @logit
    def describe_objective(self, key):
        """Get objective description."""
        return self._backend.describe(schemas.AssetType.Objective, key)

    @logit
    def leaderboard(self, objective_key, sort='desc'):
        """Get objective leaderboard"""
        return self._backend.leaderboard(objective_key, sort='desc')

    @logit
    def cancel_compute_plan(self, compute_plan_id):
        """Cancel execution of compute plan."""
        return self._backend.cancel_compute_plan(compute_plan_id)
