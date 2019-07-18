from copy import deepcopy
import logging
import os

from substra.sdk.config import ConfigManager
from substra.sdk import requests_wrapper, utils, exceptions, assets

logger = logging.getLogger(__name__)
SIMPLE_ASSETS = [assets.DATA_SAMPLE, assets.TRAINTUPLE, assets.TESTTUPLE]


class Client(object):
    def __init__(self):
        self._configManager = ConfigManager()
        self.config = self._configManager.get('default')

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

    def _get_url(self, *parts):
        """Build url from config and list of strings."""
        url_parts = [self.config['url']]
        url_parts.extend(parts)
        url = '/'.join(url_parts)
        return f'{url}/'  # django requires a suffix /

    def _get_asset_url(self, asset_name, *parts):
        """Build url from config and list of strings."""
        asset_name = assets.to_server_name(asset_name)
        parts = list(parts)
        parts.insert(0, asset_name)
        return self._get_url(*parts)

    def _post(self, asset, url, data, files, timeout):
        """Helper to do a POST request to the backend.

        In case of timeout, block till object is created.
        """
        try:
            res = requests_wrapper.post(self.config, url, data, files=files)

        except exceptions.RequestTimeout as e:
            # XXX could be handled directly by the backend (async create)
            logger.warning(
                'Request timeout, will block till asset is available')
            key = e.pkhash
            is_many = isinstance(key, list)
            if not timeout or is_many:
                # FIXME timeout on many objects is too complicated to handle.
                #       avoid operation on many objects:
                #       https://github.com/SubstraFoundation/substra-sdk-py/issues/25
                raise e
            # TODO retry only on NotFound exceptions when backend has been fixed:
            #      https://github.com/SubstraFoundation/substrabac/issues/196
            retry = utils.retry_on_exception(
                exceptions=(exceptions.NotFound, exceptions.InvalidRequest),
                timeout=float(timeout),
            )
            res = retry(self.get)(asset, key)

        return res

    def _add(self, asset, data, files=None, dryrun=False, timeout=False):
        """Add asset."""
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        files = files or {}
        if 'permissions' not in data:
            data['permissions'] = 'all'

        if dryrun:
            data['dryrun'] = True

        url = self._get_asset_url(asset)
        return self._post(asset, url, data, files, timeout)

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

    def _get(self, asset, asset_key):
        """Get asset by key."""
        url = self._get_asset_url(asset, asset_key)
        return requests_wrapper.get(self.config, url)

    def get_algo(self, algo_key):
        """Get algo by key."""
        return self._get(assets.ALGO, algo_key)

    def get_dataset(self, dataset_key):
        """Get dataset by key."""
        return self._get(assets.DATASET, dataset_key)

    def get_objective(self, objective_key):
        """Get objective by key."""
        return self._get(assets.OBJECTIVE, objective_key)

    def get_testtuple(self, testtuple_key):
        """Get testtuple by key."""
        return self._get(assets.TESTTUPLE, testtuple_key)

    def get_traintuple(self, traintuple_key):
        """Get traintuple by key."""
        return self._get(assets.TRAINTUPLE, traintuple_key)

    def _list(self, asset, filters=None, is_complex=False):
        """List assets."""
        kwargs = {}
        if filters:
            kwargs['params'] = utils.parse_filters(filters)

        url = self._get_asset_url(asset)
        result = requests_wrapper.get(self.config, url, **kwargs)
        if not is_complex and asset not in SIMPLE_ASSETS:
            result = utils.flatten(result)
        return result

    def list_algo(self, filters=None, is_complex=False):
        """List algos."""
        return self._list(assets.ALGO, filters=filters, is_complex=is_complex)

    def list_data_sample(self, filters=None, is_complex=False):
        """List data samples."""
        return self._list(assets.DATA_SAMPLE, filters=filters, is_complex=is_complex)

    def list_dataset(self, filters=None, is_complex=False):
        """List datasets."""
        return self._list(assets.DATASET, filters=filters, is_complex=is_complex)

    def list_objective(self, filters=None, is_complex=False):
        """List objectives."""
        return self._list(assets.OBJECTIVE, filters=filters, is_complex=is_complex)

    def list_testtuple(self, filters=None, is_complex=False):
        """List testtuples."""
        return self._list(assets.TESTTUPLE, filters=filters, is_complex=is_complex)

    def list_traintuple(self, filters=None, is_complex=False):
        """List traintuples."""
        return self._list(assets.TRAINTUPLE, filters=filters, is_complex=is_complex)

    def update_dataset(self, dataset_key, data):
        """Update dataset."""
        url = self._get_asset_url(assets.DATASET, dataset_key, 'update_ledger')
        return requests_wrapper.post(self.config, url, data)

    def link_dataset_with_objective(self, dataset_key, objective_key):
        """Link dataset with objective."""
        return self.update_dataset(
            dataset_key, {'objective_key': objective_key, })

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        """Link dataset with data samples."""
        url = self._get_asset_url(assets.DATA_SAMPLE, 'bulk_update')
        data = {
            'data_manager_keys': [dataset_key],
            'data_sample_keys': data_sample_keys,
        }
        return requests_wrapper.post(self.config, url, data)

    def _download(self, url, destination_folder, default_filename):
        """Download request content in destination file.

        Destination folder must exist.
        """
        r = requests_wrapper.raw_get(self.config, url, stream=True)

        destination_filename = utils.response_get_destination_filename(r)
        if not destination_filename:
            destination_filename = default_filename
        destination_path = os.path.join(destination_folder,
                                        destination_filename)

        chunk_size = 1024
        with open(destination_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size):
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
        data = self._get(asset, asset_key)
        url = data['description']['storageAddress']
        r = requests_wrapper.raw_get(self.config, url)
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
