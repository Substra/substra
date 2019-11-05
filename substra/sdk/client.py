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
import logging
import os

import keyring

from substra.sdk import utils, assets, rest_client, exceptions
from substra.sdk import config as cfg
from substra.sdk import user as usr

logger = logging.getLogger(__name__)


def get_asset_key(data):
    return data.get('pkhash') or data.get('key')


class Client(object):

    def __init__(self, config_path=None, profile_name=None, user_path=None):
        self._cfg_manager = cfg.Manager(config_path or cfg.DEFAULT_PATH)
        self._usr_manager = usr.Manager(user_path or usr.DEFAULT_PATH)
        self._current_profile = None
        self._profiles = {}
        self.client = rest_client.Client()
        self._profile_name = 'default'

        if profile_name:
            self._profile_name = profile_name
            self.set_profile(profile_name)

        # set current logged user if exists
        self.set_user()

    def login(self):
        """Login.

        Allow to login to a remote server.

        After setting your configuration with `substra config` using `-u` and `-p`
        Launch `substra login`
        You will get a token which will be stored by default in `~/.substra-user`
        You can change that thanks to the --user option (works like the --profile option)

        """

        res = self.client.login()
        token = res.json()['token']
        self._current_profile.update({
            'token': token,
        })
        self.client.set_config(self._current_profile, self._profile_name)
        return token

    def _set_current_profile(self, profile_name, profile):
        """Set client current profile."""
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

    def _add(self, asset, data, files=None, timeout=False, exist_ok=False,
             json_encoding=False):
        """Add asset."""
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        files = files or {}

        # XXX workaround because backend accepts only Form Data body. This is due to the
        #     fact that backend expects both file objects and payload in the same request
        if 'permissions' not in data:
            data['permissions_public'] = False
            data['permissions_authorized_ids'] = []
        else:
            data['permissions_public'] = data['permissions']['public']
            data['permissions_authorized_ids'] = data['permissions'].get('authorized_ids', [])
            del data['permissions']

        requests_kwargs = {}
        if files:
            requests_kwargs['files'] = files
        if json_encoding:
            requests_kwargs['json'] = data
        else:
            requests_kwargs['data'] = data

        return self.client.add(
            asset,
            retry_timeout=timeout,
            exist_ok=exist_ok,
            **requests_kwargs)

    def _add_data_samples(self, data, local=True, timeout=False):
        """Create new data sample(s) asset."""
        if not local:
            return self._add(
                assets.DATA_SAMPLE, data,
                timeout=timeout, exist_ok=False)
        with utils.extract_data_sample_files(data) as (data, files):
            return self._add(
                assets.DATA_SAMPLE, data,
                files=files, timeout=timeout, exist_ok=False)

    def add_data_sample(self, data, local=True, timeout=False,
                        exist_ok=False):
        """Create new data sample asset.

        `data` is a dict object with the following schema:

```
        {
            "path": str,
            "data_manager_keys": list[str],
            "test_only": bool,
        }
```

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        if 'paths' in data:
            raise ValueError("data: invalid 'paths' field")
        if 'path' not in data:
            raise ValueError("data: missing 'path' field")
        try:
            data_samples = self._add_data_samples(
                data, local=local, timeout=timeout)
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

    def add_data_samples(self, data, local=True, timeout=False):
        """Create many data sample assets.

        `data` is a dict object with the following schema:

```
        {
            "paths": list[str],
            "data_manager_keys": list[str],
            "test_only": bool,
        }
```
        """
        if 'path' in data:
            raise ValueError("data: invalid 'path' field")
        if 'paths' not in data:
            raise ValueError("data: missing 'paths' field")
        return self._add_data_samples(
            data, local=local, timeout=timeout)

    def add_dataset(self, data, timeout=False, exist_ok=False):
        """Create new dataset asset.

        `data` is a dict object with the following schema:

```
        {
            "name": str,
            "description": str,
            "type": str,
            "data_opener": str,
            "objective_keys": list[str],
            "permissions": {
                "public": bool,
                "authorized_ids": list[str],
            },
        }
```

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        attributes = ['data_opener', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(
                assets.DATASET, data, files=files, timeout=timeout,
                exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_dataset(get_asset_key(res))

    def add_objective(self, data, timeout=False, exist_ok=False):
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

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        attributes = ['metrics', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(
                assets.OBJECTIVE, data, files=files, timeout=timeout,
                exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_objective(get_asset_key(res))

    def add_algo(self, data, timeout=False, exist_ok=False):
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

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        attributes = ['file', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            res = self._add(
                assets.ALGO, data, files=files, timeout=timeout,
                exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_algo(get_asset_key(res))

    def add_traintuple(self, data, timeout=False, exist_ok=False):
        """Create new traintuple asset.

        `data` is a dict object with the following schema:

```
        {
            "algo_key": str,
            "objective_key": str,
            "data_manager_key": str,
            "train_data_sample_keys": list[str],
            "in_models_keys": list[str],
            "tag": str,
            "compute_plan_id": str,
        }
```

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        res = self._add(assets.TRAINTUPLE, data, timeout=timeout,
                        exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_traintuple(get_asset_key(res))

    def add_testtuple(self, data, timeout=False, exist_ok=False):
        """Create new testtuple asset.

        `data` is a dict object with the following schema:

```
        {
            "data_manager_key": str,
            "traintuple_key": str,
            "test_data_sample_keys": list[str],
            "tag": str,
            "compute_plan_id": str,
        }
```

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        res = self._add(assets.TESTTUPLE, data, timeout=timeout,
                        exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_testtuple(get_asset_key(res))

    def add_compute_plan(self, data, timeout=False):
        """Create compute plan.

        Data is a dict object with the following schema:

```
        {
            "algo_key": str,
            "objective_key": str,
            "traintuples": list[{
                "data_manager_key": str,
                "train_data_sample_keys": list[str],
                "traintuple_id": str,
                "in_models_ids": list[str],
                "tag": str,
            }],
            "testtuples": list[{
                "data_manager_key": str,
                "test_data_sample_keys": list[str],
                "testtuple_id": str,
                "traintuple_id": str,
                "tag": str,
            }]
        }
```

        """
        return self._add(assets.COMPUTE_PLAN, data, timeout=timeout, json_encoding=True)

    def get_algo(self, algo_key):
        """Get algo by key."""
        return self.client.get(assets.ALGO, algo_key)

    def get_dataset(self, dataset_key):
        """Get dataset by key."""
        return self.client.get(assets.DATASET, dataset_key)

    def get_objective(self, objective_key):
        """Get objective by key."""
        return self.client.get(assets.OBJECTIVE, objective_key)

    def get_testtuple(self, testtuple_key):
        """Get testtuple by key."""
        return self.client.get(assets.TESTTUPLE, testtuple_key)

    def get_traintuple(self, traintuple_key):
        """Get traintuple by key."""
        return self.client.get(assets.TRAINTUPLE, traintuple_key)

    def list_algo(self, filters=None, is_complex=False):
        """List algos."""
        return self.client.list(assets.ALGO, filters=filters)

    def list_data_sample(self, filters=None, is_complex=False):
        """List data samples."""
        return self.client.list(assets.DATA_SAMPLE, filters=filters)

    def list_dataset(self, filters=None, is_complex=False):
        """List datasets."""
        return self.client.list(assets.DATASET, filters=filters)

    def list_objective(self, filters=None, is_complex=False):
        """List objectives."""
        return self.client.list(assets.OBJECTIVE, filters=filters)

    def list_testtuple(self, filters=None, is_complex=False):
        """List testtuples."""
        return self.client.list(assets.TESTTUPLE, filters=filters)

    def list_traintuple(self, filters=None, is_complex=False):
        """List traintuples."""
        return self.client.list(assets.TRAINTUPLE, filters=filters)

    def list_node(self, *args, **kwargs):
        """List nodes."""
        return self.client.list(assets.NODE)

    def update_dataset(self, dataset_key, data):
        """Update dataset."""
        return self.client.request(
            'post',
            assets.DATASET,
            path=f"{dataset_key}/update_ledger/",
            data=data,
        )

    def link_dataset_with_objective(self, dataset_key, objective_key):
        """Link dataset with objective."""
        return self.update_dataset(
            dataset_key, {'objective_key': objective_key, })

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

    def download_dataset(self, asset_key, destination_folder):
        """Download data manager resource.

        Download opener script in destination folder.
        """
        data = self.get_dataset(asset_key)
        # download opener file
        default_filename = 'opener.py'
        url = data['opener']['storageAddress']
        self._download(url, destination_folder, default_filename)

    def download_algo(self, asset_key, destination_folder):
        """Download algo resource.

        Download algo package in destination folder.
        """
        data = self.get_algo(asset_key)
        # download algo package
        default_filename = 'algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

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

    def describe_algo(self, asset_key):
        """Get algo description."""
        return self._describe(assets.ALGO, asset_key)

    def describe_dataset(self, asset_key):
        """Get dataset description."""
        return self._describe(assets.DATASET, asset_key)

    def describe_objective(self, asset_key):
        """Get objective description."""
        return self._describe(assets.OBJECTIVE, asset_key)

    def leaderboard(self, objective_key, sort='desc'):
        """Get objective leaderboard"""
        return self.client.request('get', assets.OBJECTIVE, f'{objective_key}/leaderboard',
                                   params={'sort': sort})
