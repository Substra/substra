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
    """Client to interact with a Substra node.

    Args:
        config_path (str, optional): The path to the config file to load. Defaults to '~/.substra'
        profile_name (str, optional): The name of the profile to set as current profile. Defaults
            to 'default'
        user_path (str, optional): The path to the user file to load. Defaults to '~/.substra-user'
        retry_timeout (int, optional): Number of seconds to wait before retry when an add request
            timeouts. Defaults to 300 (5min)
    """

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
        """Logs into a substra node.

        Uses the current profile's login and password to get a token from the profile's node. The
        token will then be used to authenticate all calls made to the node.

        Returns:
            string: The authentication token
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
        """Sets current profile from profile name.

        If profile_name has not been defined through the add_profile method, it is loaded
        from the config file.

        Args:
            profile_name (str): The name of the profile to set as current profile

        Returns:
            dict: The new current profile
        """
        try:
            profile = self._profiles[profile_name]
        except KeyError:
            profile = self._cfg_manager.load_profile(profile_name)

        return self._set_current_profile(profile_name, profile)

    def set_user(self):
        """Loads authentication token from user file.

        If a token is found in the user file, it will be used to authenticate all calls made to the
        node.
        """
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
        """Adds new profile and sets it as current profile.

        Args:
            profile_name (str): The name of the new profile
            username (str): The username that will be used to get an authentication token
            password (str): The password that will be used to get an authentication token
            url (str): The URL of the node
            version (str): The version of the API to use. Defaults to 0.0
            insecure (bool): If true the node's SSL certificate will not be verified. Defaults to
                False.

        Returns:
            dict: The new profile
        """
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
        """Creates a new data sample asset.

        Args:
            data (dict): Must have the following schema

                {
                    "path": str,
                    "data_manager_keys": list[str],
                    "test_only": bool,
                }

                The path in the data dictionary must point to a directory representing the
                data sample content. Note that the directory can contain multiple files, all the
                directory content will be added to the platform.

            local (bool):

                If true, path must refer to a directory located on the local
                filesystem. The file content will be transferred to the server through an
                HTTP query, so this mode should be used for relatively small files (<10mo).

                If false, path must refer to a directory located on the server
                filesystem. This directory must be accessible (readable) by the server.  This
                mode is well suited for all kind of file sizes.

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A data sample with the same content already exists on the server.
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
        """Creates multiple new data sample assets.

        This method is well suited for adding multiple small files only. For adding a
        large amount of data it is recommended to add them one by one. It allows a
        better control in case of failures.

        Args:
            data (dict): Must have the following schema

                {
                    "paths": list[str],
                    "data_manager_keys": list[str],
                    "test_only": bool,
                }

                The paths in the data dictionary must be a list of paths where each path
                points to a directory representing one data sample.

            local (bool):

                If true, path must refer to a directory located on the local
                filesystem. The file content will be transferred to the server through an
                HTTP query, so this mode should be used for relatively small files (<10mo).

                If false, path must refer to a directory located on the server
                filesystem. This directory must be accessible (readable) by the server.  This
                mode is well suited for all kind of file sizes.

        Returns:
            list[dict]: The newly created assets

        Raises:
            AlreadyExists: data samples with the same content as some of the paths already exist on
                the server.
        """
        data = _update_permissions_field(data)
        if 'path' in data:
            raise ValueError("data: invalid 'path' field")
        if 'paths' not in data:
            raise ValueError("data: missing 'paths' field")
        return self._add_data_samples(data, local=local)

    @logit
    def add_dataset(self, data, exist_ok=False):
        """Creates a new dataset asset.

        Args:
            data (dict): Must have the following schema

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

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A dataset with the same opener already exists on the server.
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
        """Creates a new objective asset.

        Args:

            data (dict): Must have the following schema

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

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: An objective with the same description already exists on the server.
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
        """Creates a new algo asset.

        Args:
            data (dict): Must have the following schema

                {
                    "name": str,
                    "description": str,
                    "file": str,
                    "permissions": {
                        "public": bool,
                        "authorized_ids": list[str],
                    },
                }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: An algo with the same archive file already exists on the server.
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
        """Creates a new aggregate algo asset.

        Args:
            data (dict): Must have the following schema

                {
                    "name": str,
                    "description": str,
                    "file": str,
                    "permissions": {
                        "public": bool,
                        "authorizedIDs": list[str],
                    },
                }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: An aggregate algo with the same archive file already exists on the
                server.
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
        """Creates a new composite algo asset.

        Args:
            data (dict): Must have the following schema

                    {
                        "name": str,
                        "description": str,
                        "file": str,
                        "permissions": {
                            "public": bool,
                            "authorizedIDs": list[str],
                        },
                    }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A composite algo with the same archive file already exists on the
                server.
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
        """Creates a new traintuple asset.

        Args:
            data (dict): Must have the following schema

                {
                    "algo_key": str,
                    "data_manager_key": str,
                    "train_data_sample_keys": list[str],
                    "in_models_keys": list[str],
                    "tag": str,
                    "rank": int,
                    "compute_plan_id": str,
                }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A traintuple already exists on the server that:

                * has the same algo_key, data_manager_key, train_data_sample_keys and in_models_keys
                * was created through the same node this Client instance points to
        """
        res = self._add(assets.TRAINTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_traintuple(get_asset_key(res))

    @logit
    def add_aggregatetuple(self, data, exist_ok=False):
        """Creates a new aggregatetuple asset.

        Args:
            data (dict): Must have the following schema

                {
                    "algo_key": str,
                    "in_models_keys": list[str],
                    "tag": str,
                    "compute_plan_id": str,
                    "rank": int,
                    "worker": str,
                }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A traintuple already exists on the server that:

                * has the same algo_key and in_models_keys
                * was created through the same node this Client instance points to
        """
        res = self._add(assets.AGGREGATETUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_aggregatetuple(get_asset_key(res))

    @logit
    def add_composite_traintuple(self, data, exist_ok=False):
        """Creates a new composite traintuple asset.

        As specified in the data dict structure, output trunk models cannot be made
        public.

        Args:
            data (dict): Must have the following schema

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

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A traintuple already exists on the server that:

                * has the same algo_key, data_manager_key, train_data_sample_keys,
                  in_head_models_key and in_trunk_model_key
                * was created through the same node this Client instance points to
        """
        data = _update_permissions_field(data, permissions_field='out_trunk_model_permissions')
        res = self._add(assets.COMPOSITE_TRAINTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_composite_traintuple(get_asset_key(res))

    @logit
    def add_testtuple(self, data, exist_ok=False):
        """Creates a new testtuple asset.

        Args:
            data (dict): Must have the following schema

                {
                    "objective_key": str,
                    "data_manager_key": str,
                    "traintuple_key": str,
                    "test_data_sample_keys": list[str],
                    "tag": str,
                }

            exist_ok (bool, optional): If true, AlreadyExists exceptions will be ignored and the
                existing asset will be returned. Defaults to False.

        Returns:
            dict: The newly created asset.

        Raises:
            AlreadyExists: A traintuple already exists on the server that:

                * has the same traintuple_key, objective_key, data_manager_key and
                  test_data_sample_keys
                * was created through the same node this Client instance points to
        """
        res = self._add(assets.TESTTUPLE, data, exist_ok=exist_ok)

        # The backend has inconsistent API responses when getting or adding an asset (with much
        # less data when responding to adds). A second GET request hides the discrepancies.
        return self.get_testtuple(get_asset_key(res))

    @logit
    def add_compute_plan(self, data):
        """Creates a new compute plan asset.

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.

        Args:
            data (dict): Must have the following schema

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

        Returns:
            dict: The newly created asset.
        """
        return self._add(assets.COMPUTE_PLAN, data, json_encoding=True)

    @logit
    def get_algo(self, algo_key):
        """Gets an algo by key.

        Args:
            algo_key (str): The key of the algo

        Raises:
            NotFound: The algo_key did not match any algo.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.ALGO, algo_key)

    @logit
    def get_compute_plan(self, compute_plan_key):
        """Gets a compute plan by key.

        Args:
            compute_plan_key (str): The key of the compute plan

        Raises:
            NotFound: The compute_plan_key did not match any compute plan.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.COMPUTE_PLAN, compute_plan_key)

    @logit
    def get_aggregate_algo(self, aggregate_algo_key):
        """Gets an aggregate algo by key.

        Args:
            aggregate_algo_key (str): The key of the aggregate algo

        Raises:
            NotFound: The aggregate_algo_key did not match any aggregate algo.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.AGGREGATE_ALGO, aggregate_algo_key)

    @logit
    def get_composite_algo(self, composite_algo_key):
        """Gets a composite algo by key.

        Args:
            composite_algo_key (str): The key of the composite algo

        Raises:
            NotFound: The composite_algo_key did not match any composite algo.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.COMPOSITE_ALGO, composite_algo_key)

    @logit
    def get_dataset(self, dataset_key):
        """Gets a dataset by key.

        Args:
            dataset_key (str): The key of the dataset

        Raises:
            NotFound: The dataset_key did not match any dataset.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.DATASET, dataset_key)

    @logit
    def get_objective(self, objective_key):
        """Gets an objective by key.

        Args:
            objective_key (str): The key of the objective

        Raises:
            NotFound: The objective_key did not match any objective.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.OBJECTIVE, objective_key)

    @logit
    def get_testtuple(self, testtuple_key):
        """Gets a testtuple by key.

        Args:
            testtuple_key (str): The key of the testtuple

        Raises:
            NotFound: The testtuple_key did not match any testtuple.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.TESTTUPLE, testtuple_key)

    @logit
    def get_traintuple(self, traintuple_key):
        """Gets a traintuple by key.

        Args:
            traintuple_key (str): The key of the traintuple

        Raises:
            NotFound: The traintuple_key did not match any traintuple.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.TRAINTUPLE, traintuple_key)

    @logit
    def get_aggregatetuple(self, aggregatetuple_key):
        """Gets an aggregatetuple by key.

        Args:
            aggregatetuple_key (str): The key of the aggregatetuple

        Raises:
            NotFound: The aggregatetuple_key did not match any aggregatetuple.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.AGGREGATETUPLE, aggregatetuple_key)

    @logit
    def get_composite_traintuple(self, composite_traintuple_key):
        """Gets a composite traintuple by key.

        Args:
            composite_traintuple_key (str): The key of the composite_traintuple

        Raises:
            NotFound: The composite_traintuple_key did not match any composite_traintuple.

        Returns:
            dict: The requested asset
        """
        return self.client.get(assets.COMPOSITE_TRAINTUPLE, composite_traintuple_key)

    @logit
    def list_algo(self, filters=None, is_complex=False):
        """Lists algos.

        Args:
            filters (list[str], optional): List of filters to apply to the algo list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.ALGO, filters=filters)

    @logit
    def list_compute_plan(self, filters=None, is_complex=False):
        """Lists compute plans.

        Args:
            filters (list[str], optional): List of filters to apply to the compute plan list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.COMPUTE_PLAN, filters=filters)

    @logit
    def list_aggregate_algo(self, filters=None, is_complex=False):
        """Lists aggregate algos.

        Args:
            filters (list[str], optional): List of filters to apply to the aggregate algo list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.AGGREGATE_ALGO, filters=filters)

    @logit
    def list_composite_algo(self, filters=None, is_complex=False):
        """Lists composite algos.

        Args:
            filters (list[str], optional): List of filters to apply to the composite algo list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.COMPOSITE_ALGO, filters=filters)

    @logit
    def list_data_sample(self, filters=None, is_complex=False):
        """Lists data samples.

        Args:
            filters (list[str], optional): List of filters to apply to the data sample list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.DATA_SAMPLE, filters=filters)

    @logit
    def list_dataset(self, filters=None, is_complex=False):
        """Lists datasets.

        Args:
            filters (list[str], optional): List of filters to apply to the dataset list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.DATASET, filters=filters)

    @logit
    def list_objective(self, filters=None, is_complex=False):
        """Lists objectives.

        Args:
            filters (list[str], optional): List of filters to apply to the objective list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.OBJECTIVE, filters=filters)

    @logit
    def list_testtuple(self, filters=None, is_complex=False):
        """Lists testtuple

        Args:
            filters (list[str], optional): List of filters to apply to the testtuple list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.TESTTUPLE, filters=filters)

    @logit
    def list_traintuple(self, filters=None, is_complex=False):
        """Lists traintuples.

        Args:
            filters (list[str], optional): List of filters to apply to the traintuple list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.TRAINTUPLE, filters=filters)

    @logit
    def list_aggregatetuple(self, filters=None, is_complex=False):
        """Lists aggregatetuples.

        Args:
            filters (list[str], optional): List of filters to apply to the aggregatetuple list.
                Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.AGGREGATETUPLE, filters=filters)

    @logit
    def list_composite_traintuple(self, filters=None, is_complex=False):
        """Lists composite traintuples.

        Args:
            filters (list[str], optional): List of filters to apply to the composite traintuple
                list. Defaults to None.

                A single filter is a string that can be either:
                * 'OR'
                * '<asset_type>:<asset_field>:<value>'

        Raises:
            InvalidRequest:

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.COMPOSITE_TRAINTUPLE, filters=filters)

    @logit
    def list_node(self, *args, **kwargs):
        """Lists nodes.

        Returns:
            list[dict]: The list of requested assets.
        """
        return self.client.list(assets.NODE)

    @logit
    def update_dataset(self, dataset_key, data):
        """Updates a dataset.

        This only updates the link between a given dataset and objectives.

        Args:
            dataset_key (str): The dataset key of the asset to update.
            data (dict): Must have the following schema

                {
                    "objective_key": str
                }

        Returns:
            dict: The updated asset.
        """
        return self.client.request(
            'post',
            assets.DATASET,
            path=f"{dataset_key}/update_ledger/",
            data=data,
        )

    @logit
    def update_compute_plan(self, compute_plan_id, data):
        """Updates an existing compute plan asset.

        As specified in the data dict structure, output trunk models of composite
        traintuples cannot be made public.

        Args:
            compute_plan_id (str): The compute plan ID of the asset to update.
            data (dict): Must have the following schema

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
                }

        Returns:
            dict: The updated asset.
        """
        return self.client.request(
            'post',
            assets.COMPUTE_PLAN,
            path=f"{compute_plan_id}/update_ledger/",
            json=data,
        )

    @logit
    def link_dataset_with_objective(self, dataset_key, objective_key):
        """Links a dataset with an objective.

        Args:
            dataset_key (str): The key of the dataset to link.
            objective_key (str): The key of the objective to link.

        Returns:
            dict: The updated dataset.
        """
        return self.update_dataset(
            dataset_key, {'objective_key': objective_key, })

    @logit
    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        """Links a dataset with data samples.

        Args:
            dataset_key (str): The key of the dataset to link.
            data_sample_keys (list[str]): The keys of the data samples to link.

        Returns:
            list[dict]: The updated data samples.
        """
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
    def download_dataset(self, dataset_key, destination_folder):
        """Downloads a dataset opener.

        Args:
            dataset_key (str): The key of the target dataset.
            destination_folder (str): The path to the folder where the target dataset's opener
                should be downloaded.
        """
        data = self.get_dataset(dataset_key)
        # download opener file
        default_filename = 'opener.py'
        url = data['opener']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_algo(self, algo_key, destination_folder):
        """Downloads an algo archive.

        Args:
            algo_key (str): The key of the target algo.
            destination_folder (str): The path to the folder where the target algo's archive
                should be downloaded.
        """
        data = self.get_algo(algo_key)
        # download algo package
        default_filename = 'algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_aggregate_algo(self, aggregate_algo_key, destination_folder):
        """Downloads an aggregate algo archive.

        Args:
            aggregate_algo_key (str): The key of the target aggregate algo.
            destination_folder (str): The path to the folder where the target aggregate algo's
                archive should be downloaded.
        """
        data = self.get_aggregate_algo(aggregate_algo_key)
        # download aggregate algo package
        default_filename = 'aggregate_algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_composite_algo(self, composite_algo_key, destination_folder):
        """Downloads a composite algo archive.

        Args:
            composite_algo_key (str): The key of the target composite algo.
            destination_folder (str): The path to the folder where the target composite algo's
                archive should be downloaded.
        """
        data = self.get_composite_algo(composite_algo_key)
        # download composite algo package
        default_filename = 'composite_algo.tar.gz'
        url = data['content']['storageAddress']
        self._download(url, destination_folder, default_filename)

    @logit
    def download_objective(self, objective_key, destination_folder):
        """Downloads an objective metrics archive.

        Args:
            objective_key (str): The key of the target objective.
            destination_folder (str): The path to the folder where the target objective's
                metrics archive should be downloaded.
        """
        data = self.get_objective(objective_key)
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
    def describe_algo(self, algo_key):
        """Gets an algo description.

        Args:
            algo_key (str): The key of the target algo.

        Returns:
            str: The asset's description.
        """
        return self._describe(assets.ALGO, algo_key)

    @logit
    def describe_aggregate_algo(self, aggregate_algo_key):
        """Gets an aggregate algo description.

        Args:
            aggregate_algo_key (str): The key of the target aggregate algo.

        Returns:
            str: The asset's description.
        """
        return self._describe(assets.AGGREGATE_ALGO, aggregate_algo_key)

    @logit
    def describe_composite_algo(self, composite_algo_key):
        """Gets a composite algo description.

        Args:
            composite_algo_key (str): The key of the target composite algo.

        Returns:
            str: The asset's description.
        """
        return self._describe(assets.COMPOSITE_ALGO, composite_algo_key)

    @logit
    def describe_dataset(self, dataset_key):
        """Gets a dataset description.

        Args:
            dataset_key (str): The key of the target dataset.

        Returns:
            str: The asset's description.
        """
        return self._describe(assets.DATASET, dataset_key)

    @logit
    def describe_objective(self, objective_key):
        """Gets an objective description.

        Args:
            objective_key (str): The key of the target objective.

        Returns:
            str: The asset's description.
        """
        return self._describe(assets.OBJECTIVE, objective_key)

    @logit
    def leaderboard(self, objective_key, sort='desc'):
        """Gets an objective leaderboard

        Args:
            objective_key (str): The key of the target objective.
            sort (str): Either 'desc' or 'asc'. Whether to sort the leaderboard values by ascending
                order (lowest score first) or descending order (highest score first). Defaults to
                'desc'

        Returns:
            list[dict]: The list of leaderboard tuples.

        """
        return self.client.request('get', assets.OBJECTIVE, f'{objective_key}/leaderboard',
                                   params={'sort': sort})

    @logit
    def cancel_compute_plan(self, compute_plan_id):
        """Cancels the execution of a compute plan.

        Args:
            compute_plan_id (str): The ID of the compute plan to cancel.

        Returns:
            dict: The canceled compute plan.
        """
        return self.client.request(
            'post',
            assets.COMPUTE_PLAN,
            path=f"{compute_plan_id}/cancel",
        )
