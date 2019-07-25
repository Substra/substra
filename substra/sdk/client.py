from copy import deepcopy
import logging
import os

from substra.sdk.config import ConfigManager
from substra.sdk import utils, assets, rest_client

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self):
        self._configManager = ConfigManager()
        self.config = self._configManager.get('default')
        self.client = rest_client.Client(self.config)

    def create_config(self, profile, url='http://127.0.0.1:8000',
                      version='0.0', auth=False, insecure=False):
        """Create new config profile."""
        return self._configManager.create(profile=profile,
                                          url=url,
                                          version=version,
                                          auth=auth,
                                          insecure=insecure)

    def set_config(self, profile='default'):
        """Set config profile."""
        self.config = self._configManager.get(profile)
        return self.config

    def get_config(self):
        """Get current config profile."""
        return self.config

    def _add(self, asset, data, files=None, dryrun=False, timeout=False):
        """Add asset."""
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        files = files or {}
        if 'permissions' not in data:
            data['permissions'] = 'all'

        if dryrun:
            data['dryrun'] = True

        return self.client.add(asset, retry_timeout=timeout, data=data, files=files)

    def add_data_sample(self, data, local=True, dryrun=False, timeout=False):
        """Create new data sample asset(s)."""
        if not local:
            return self._add(assets.DATA_SAMPLE, data, dryrun=dryrun, timeout=timeout)

        with utils.extract_data_sample_files(data) as (data, files):
            return self._add(
                assets.DATA_SAMPLE, data, files=files, dryrun=dryrun, timeout=timeout)

    def add_dataset(self, data, dryrun=False, timeout=False):
        """Create new dataset asset."""
        attributes = ['data_opener', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            return self._add(
                assets.DATASET, data, files=files, dryrun=dryrun, timeout=timeout)

    def add_objective(self, data, dryrun=False, timeout=False):
        """Create new objective asset."""
        attributes = ['metrics', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            return self._add(
                assets.OBJECTIVE, data, files=files, dryrun=dryrun, timeout=timeout)

    def add_algo(self, data, dryrun=False, timeout=False):
        """Create new algo asset."""
        attributes = ['file', 'description']
        with utils.extract_files(data, attributes) as (data, files):
            return self._add(
                assets.ALGO, data, files=files, dryrun=dryrun, timeout=timeout)

    def add_traintuple(self, data, dryrun=False, timeout=False):
        """Create new traintuple asset."""
        return self._add(assets.TRAINTUPLE, data, dryrun=dryrun, timeout=timeout)

    def add_testtuple(self, data, dryrun=False, timeout=False):
        """Create new testtuple asset."""
        return self._add(assets.TESTTUPLE, data, dryrun=dryrun, timeout=timeout)

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
