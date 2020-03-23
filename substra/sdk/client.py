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

from copy import deepcopy
import functools
import logging
import os
import time

import keyring

from substra.sdk import utils, assets, rest_client, exceptions
from substra.sdk import config as cfg
from substra.sdk import user as usr

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


def get_asset_key(data):
    return data.get('pkhash') or data.get('key')


def _flatten_permissions(data, field_name):
    data = deepcopy(data)

    p = data[field_name]  # should not raise as a default permissions is added if missing
    data[f'{field_name}_public'] = p['public']
    data[f'{field_name}_authorized_ids'] = p.get('authorized_ids', [])
    del data[field_name]

    return data


def _update_permissions_field(data, permissions_field='permissions'):
    if permissions_field not in data:
        default_permissions = {
            'public': False,
            'authorized_ids': [],
        }
        data[permissions_field] = default_permissions
    # XXX workaround because backend accepts only Form Data body. This is due to
    #     the fact that backend expects both file objects and payload in the
    #     same request
    data = _flatten_permissions(data, field_name=permissions_field)
    return data


class Client(object):

    def __init__(self, config_path=None, profile_name=None, user_path=None,
                 retry_timeout=DEFAULT_RETRY_TIMEOUT):
        self._cfg_manager = cfg.Manager(config_path or cfg.DEFAULT_PATH)
        self._usr_manager = usr.Manager(user_path or usr.DEFAULT_PATH)
        self._current_profile = None
        self._profiles = {}
        self.client = rest_client.Client()
        self._profile_name = 'default'
        self._retry_timeout = retry_timeout

        if profile_name:
            self._profile_name = profile_name
            self.set_profile(profile_name)

        # set current logged user if exists
        self.set_user()

    @logit
    def login(self):
        """Login.

        Allow to login to a remote server.

        After setting your configuration with `substra config` using `-u` and `-p`
        Launch `substra login`
        You will get a token which will be stored by default in `~/.substra-user`
        You can change that thanks to the --user option (works like the --profile option)

        """

        if not self._current_profile:
            raise exceptions.SDKException("No profile defined")

        res = self.client.login()
        token = res.json()['token']
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

        return profile

    def set_profile(self, profile_name):
        """Set profile from profile name.

        If profiles has not been defined through the `add_profile` method, it is loaded
        from the config file.
        """
        try:
            profile = self._profiles[profile_name]
        except KeyError:
            profile = self._cfg_manager.load_profile(profile_name)

        return self._set_current_profile(profile_name, profile)

    def set_user(self):
        try:
            user = self._usr_manager.load_user()
        except (exceptions.UserException, FileNotFoundError):
            pass
        else:
            if self._current_profile is not None and 'token' in user:
                self._current_profile.update({
                    'token': user['token'],
                })
                self.client.set_config(self._current_profile, self._profile_name)

    def add_profile(self, profile_name, username, password, url, version='0.0', insecure=False):
        """Add new profile (in-memory only)."""
        profile = cfg.create_profile(
            url=url,
            version=version,
            insecure=insecure,
            username=username,
        )
        keyring.set_password(profile_name, username, password)
        return self._set_current_profile(profile_name, profile)

    def _add(self, asset, data, files=None, exist_ok=False, json_encoding=False):
        """Add asset."""
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        files = files or {}
        requests_kwargs = {}
        if files:
            requests_kwargs['files'] = files
        if json_encoding:
            requests_kwargs['json'] = data
        else:
            requests_kwargs['data'] = data

        return self.client.add(
            asset,
            retry_timeout=self._retry_timeout,
            exist_ok=exist_ok,
            **requests_kwargs)

    def _add_data_samples(self, data, local=True):
        """Create new data sample(s) asset."""
        if not local:
            return self._add(
                assets.DATA_SAMPLE, data,
                exist_ok=False)
        with utils.extract_data_sample_files(data) as (data, files):
            return self._add(
                assets.DATA_SAMPLE, data,
                files=files, exist_ok=False)

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
        data = _update_permissions_field(data)
        if 'paths' in data:
            raise ValueError("data: invalid 'paths' field")
        if 'path' not in data:
            raise ValueError("data: missing 'path' field")
        try:
            data_samples = self._add_data_samples(data, local=local)
        except exceptions.AlreadyExists as e:
            # exist_ok option must be handle separately for data samples as a get action
            # is not allowed on data samples
            if not exist_ok:
                raise
            key = e.pkhash[0]
            logger.warning(f"data_sample already exists: key='{key}'")
            data_samples = [{'pkhash': key}]
        # there is currently a single route in the backend to add a single or many
        # datasamples, this route always returned a list of created data sample keys
        return data_samples[0]

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
        data = _update_permissions_field(data)
        if 'path' in data:
            raise ValueError("data: invalid 'path' field")
        if 'paths' not in data:
            raise ValueError("data: missing 'paths' field")
        return self._add_data_samples(data, local=local)

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
        }
```

        If a dataset with the same opener already exists, an `AlreadyExists` exception will be
        raised.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        data = _update_permissions_field(data)
        attributes = ['data_opener', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(assets.DATASET, data, files=files, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_dataset(get_asset_key(res))

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
        }
```

        If an objective with the same description already exists, an `AlreadyExists` exception will
        be raised.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        data = _update_permissions_field(data)
        attributes = ['metrics', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(assets.OBJECTIVE, data, files=files, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_objective(get_asset_key(res))

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
        }
```

        If an algo with the same archive file already exists, an `AlreadyExists` exception will be
        raised.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        data = _update_permissions_field(data)
        attributes = ['file', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(assets.ALGO, data, files=files, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_algo(get_asset_key(res))

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
        }
```
        If an aggregate algo with the same archive file already exists, an `AlreadyExists`
        exception will be raised.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        data = _update_permissions_field(data)
        attributes = ['file', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(assets.AGGREGATE_ALGO, data, files=files, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_aggregate_algo(get_asset_key(res))

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
        }
```
        If a composite algo with the same archive file already exists, an `AlreadyExists` exception
        will be raised.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        data = _update_permissions_field(data)
        attributes = ['file', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(assets.COMPOSITE_ALGO, data, files=files, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_composite_algo(get_asset_key(res))

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
        res = self._add(assets.TRAINTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_traintuple(get_asset_key(res))

    @logit
    def add_aggregatetuple(self, data, exist_ok=False):
        """Create new aggregatetuple asset.
        `data` is a dict object with the following schema:
```
        {
            "algo_key": str,
            "in_models_keys": list[str],
            "tag": str,
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
        res = self._add(assets.AGGREGATETUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_aggregatetuple(get_asset_key(res))

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
        data = _update_permissions_field(data, permissions_field='out_trunk_model_permissions')
        res = self._add(assets.COMPOSITE_TRAINTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_composite_traintuple(get_asset_key(res))

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
        }
```

        An `AlreadyExists` exception will be raised if a traintuple already exists that:
        * has the same `traintuple_key`, `objective_key`, `data_manager_key` and
          `test_data_sample_keys`
        * and was created through the same node you are using

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        res = self._add(assets.TESTTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_testtuple(get_asset_key(res))

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
            }]
            "aggregatetuples": list[{
                "aggregatetuple_id": str,
                "algo_key": str,
                "worker": str,
                "in_models_ids": list[str],
                "tag": str,
            }],
            "testtuples": list[{
                "objective_key": str,
                "data_manager_key": str,
                "test_data_sample_keys": list[str],
                "traintuple_id": str,
                "tag": str,
            }],
            "clean_models": bool,
            "tag": str
        }
```

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.
        """
        return self._add(assets.COMPUTE_PLAN, data, json_encoding=True)

    @logit
    def get_algo(self, algo_key):
        """Get algo by key."""
        return self.client.get(assets.ALGO, algo_key)

    @logit
    def get_compute_plan(self, compute_plan_key):
        """Get compute plan by key."""
        return self.client.get(assets.COMPUTE_PLAN, compute_plan_key)

    @logit
    def get_aggregate_algo(self, aggregate_algo_key):
        """Get aggregate algo by key."""
        return self.client.get(assets.AGGREGATE_ALGO, aggregate_algo_key)

    @logit
    def get_composite_algo(self, composite_algo_key):
        """Get composite algo by key."""
        return self.client.get(assets.COMPOSITE_ALGO, composite_algo_key)

    @logit
    def get_dataset(self, dataset_key):
        """Get dataset by key."""
        return self.client.get(assets.DATASET, dataset_key)

    @logit
    def get_objective(self, objective_key):
        """Get objective by key."""
        return self.client.get(assets.OBJECTIVE, objective_key)

    @logit
    def get_testtuple(self, testtuple_key):
        """Get testtuple by key."""
        return self.client.get(assets.TESTTUPLE, testtuple_key)

    @logit
    def get_traintuple(self, traintuple_key):
        """Get traintuple by key."""
        return self.client.get(assets.TRAINTUPLE, traintuple_key)

    @logit
    def get_aggregatetuple(self, aggregatetuple_key):
        """Get aggregatetuple by key."""
        return self.client.get(assets.AGGREGATETUPLE, aggregatetuple_key)

    @logit
    def get_composite_traintuple(self, composite_traintuple_key):
        """Get composite traintuple by key."""
        return self.client.get(assets.COMPOSITE_TRAINTUPLE, composite_traintuple_key)

    @logit
    def list_algo(self, filters=None, is_complex=False):
        """List algos."""
        return self.client.list(assets.ALGO, filters=filters)

    @logit
    def list_compute_plan(self, filters=None, is_complex=False):
        """List compute plans."""
        return self.client.list(assets.COMPUTE_PLAN, filters=filters)

    @logit
    def list_aggregate_algo(self, filters=None, is_complex=False):
        """List aggregate algos."""
        return self.client.list(assets.AGGREGATE_ALGO, filters=filters)

    @logit
    def list_composite_algo(self, filters=None, is_complex=False):
        """List composite algos."""
        return self.client.list(assets.COMPOSITE_ALGO, filters=filters)

    @logit
    def list_data_sample(self, filters=None, is_complex=False):
        """List data samples."""
        return self.client.list(assets.DATA_SAMPLE, filters=filters)

    @logit
    def list_dataset(self, filters=None, is_complex=False):
        """List datasets."""
        return self.client.list(assets.DATASET, filters=filters)

    @logit
    def list_objective(self, filters=None, is_complex=False):
        """List objectives."""
        return self.client.list(assets.OBJECTIVE, filters=filters)

    @logit
    def list_testtuple(self, filters=None, is_complex=False):
        """List testtuples."""
        return self.client.list(assets.TESTTUPLE, filters=filters)

    @logit
    def list_traintuple(self, filters=None, is_complex=False):
        """List traintuples."""
        return self.client.list(assets.TRAINTUPLE, filters=filters)

    @logit
    def list_aggregatetuple(self, filters=None, is_complex=False):
        """List aggregatetuples."""
        return self.client.list(assets.AGGREGATETUPLE, filters=filters)

    @logit
    def list_composite_traintuple(self, filters=None, is_complex=False):
        """List composite traintuples."""
        return self.client.list(assets.COMPOSITE_TRAINTUPLE, filters=filters)

    @logit
    def list_node(self, *args, **kwargs):
        """List nodes."""
        return self.client.list(assets.NODE)

    @logit
    def update_dataset(self, dataset_key, data):
        """Update dataset."""
        return self.client.request(
            'post',
            assets.DATASET,
            path=f"{dataset_key}/update_ledger/",
            data=data,
        )

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
            }]
            "aggregatetuples": list[{
                "aggregatetuple_id": str,
                "algo_key": str,
                "worker": str,
                "in_models_ids": list[str],
                "tag": str,
            }],
            "testtuples": list[{
                "objective_key": str,
                "data_manager_key": str,
                "test_data_sample_keys": list[str],
                "traintuple_id": str,
                "tag": str,
            }]
        }
```

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.

        """
        return self.client.request(
            'post',
            assets.COMPUTE_PLAN,
            path=f"{compute_plan_id}/update_ledger/",
            json=data,
        )

    @logit
    def link_dataset_with_objective(self, dataset_key, objective_key):
        """Link dataset with objective."""
        return self.update_dataset(
            dataset_key, {'objective_key': objective_key, })

    @logit
    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        """Link dataset with data samples."""
        data = {
            'data_manager_keys': [dataset_key],
            'data_sample_keys': data_sample_keys,
        }
        return self.client.request(
            'post',
            assets.DATA_SAMPLE,
            path="bulk_update/",
            data=data,
        )

    def _download(self, url, destination_folder, default_filename):
        """Download request content in destination file.

        Destination folder must exist.
        """
        response = self.client.get_data(url, stream=True)

        destination_filename = utils.response_get_destination_filename(response)
        if not destination_filename:
            destination_filename = default_filename
        destination_path = os.path.join(destination_folder,
                                        destination_filename)

        chunk_size = 1024
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size):
                f.write(chunk)
        return destination_path

    @logit
    def download_dataset(self, asset_key, destination_folder):
        """Download data manager resource.

        Download opener script in destination folder.
        """
        data = self.get_dataset(asset_key)
        # download opener file
        default_filename = 'opener.py'
        url = data['opener']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_algo(self, asset_key, destination_folder):
        """Download algo resource.

        Download algo package in destination folder.
        """
        data = self.get_algo(asset_key)
        # download algo package
        default_filename = 'algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_aggregate_algo(self, asset_key, destination_folder):
        """Download aggregate algo resource.

        Download aggregate algo package in destination folder.
        """
        data = self.get_aggregate_algo(asset_key)
        # download aggregate algo package
        default_filename = 'aggregate_algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_composite_algo(self, asset_key, destination_folder):
        """Download composite algo resource.

        Download composite algo package in destination folder.
        """
        data = self.get_composite_algo(asset_key)
        # download composite algo package
        default_filename = 'composite_algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_objective(self, asset_key, destination_folder):
        """Download objective resource.

        Download metrics script in destination folder.
        """
        data = self.get_objective(asset_key)
        # download metrics script
        default_filename = 'metrics.py'
        url = data['metrics']['storageAddress']
        self._download(url, destination_folder, default_filename)

    def _describe(self, asset, asset_key):
        """Get asset description."""
        data = self.client.get(asset, asset_key)
        url = data['description']['storageAddress']
        r = self.client.get_data(url)
        return r.text

    @logit
    def describe_algo(self, asset_key):
        """Get algo description."""
        return self._describe(assets.ALGO, asset_key)

    @logit
    def describe_aggregate_algo(self, asset_key):
        """Get aggregate algo description."""
        return self._describe(assets.AGGREGATE_ALGO, asset_key)

    @logit
    def describe_composite_algo(self, asset_key):
        """Get composite algo description."""
        return self._describe(assets.COMPOSITE_ALGO, asset_key)

    @logit
    def describe_dataset(self, asset_key):
        """Get dataset description."""
        return self._describe(assets.DATASET, asset_key)

    @logit
    def describe_objective(self, asset_key):
        """Get objective description."""
        return self._describe(assets.OBJECTIVE, asset_key)

    @logit
    def leaderboard(self, objective_key, sort='desc'):
        """Get objective leaderboard"""
        return self.client.request('get', assets.OBJECTIVE, f'{objective_key}/leaderboard',
                                   params={'sort': sort})

    @logit
    def cancel_compute_plan(self, compute_plan_id):
        """Cancel execution of compute plan."""
        return self.client.request(
            'post',
            assets.COMPUTE_PLAN,
            path=f"{compute_plan_id}/cancel",
        )
