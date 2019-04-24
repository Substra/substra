import copy
import json

from substra_sdk_py import exceptions
from substra.utils import load_json_from_args

from .api import Api, DATA_SAMPLE_ASSET, DATASET_ASSET, DATA_MANAGER_ASSET, OBJECTIVE_ASSET


class Register(Api):
    """Register asset"""

    ACCEPTED_ASSETS = [DATA_SAMPLE_ASSET, DATASET_ASSET, OBJECTIVE_ASSET]

    def _add_objective(self, data, dryrun):
        print('adding objective')
        asset = OBJECTIVE_ASSET
        # add objective, do not fail on conflict
        try:
            res = self.client.add(OBJECTIVE_ASSET, data, dryrun)
        except exceptions.HTTPError as e:
            if e.response.status_code != 409:
                try:
                    error = e.response.json()
                except ValueError:
                    error = e.response.content
                raise Exception(f'Failed to create {asset}: {e}: {error}')

            res = e.response.json()

        print(json.dumps(res, indent=2), end='')
        return res['pkhash']

    def _add_data_manager(self, data, dryrun):
        print('adding data manager')
        asset = DATA_MANAGER_ASSET
        # add data manager, do not fail on conflict
        try:
            res = self.client.add(asset, data, dryrun)
        except exceptions.HTTPError as e:
            if e.response.status_code != 409:
                try:
                    error = e.response.json()
                except ValueError:
                    error = e.response.content
                raise Exception(f'Failed to create {asset}: {e}: {error}')

            res = e.response.json()

        print(json.dumps(res, indent=2), end='')
        return res['pkhash']

    def _register_data_sample(self, data, dryrun):
        print('registering data sample')
        asset = DATA_SAMPLE_ASSET
        try:
            res = self.client.register(asset, data, dryrun)
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to create {asset}: {e}: {error}')

        print(json.dumps(res, indent=2), end='')
        return res

    def run(self):
        super(Register, self).run()

        args = self.options['<args>']
        data = load_json_from_args(args)
        asset = self.get_asset_option()
        dryrun = self.options.get('--dry-run', False)

        if asset == DATA_SAMPLE_ASSET:
            self._register_data_sample(data, dryrun)

        elif asset == DATASET_ASSET:
            data_manager_data = data['data_manager']
            data_manager_key = self._add_data_manager(data_manager_data,
                                                      dryrun)

            data_sample_data = copy.deepcopy(data['data_samples'])
            data_sample_data['data_manager_keys'] = [data_manager_key]
            self._register_data_sample(data_sample_data, dryrun)

        elif asset == OBJECTIVE_ASSET:
            objective_data = data['objective']
            objective_key = self._add_objective(objective_data, dryrun)

            data_manager_data = copy.deepcopy(data['data_manager'])
            data_manager_data['objective_keys'] = [objective_key]
            data_manager_key = self._add_data_manager(data_manager_data,
                                                      dryrun)

            data_sample_data = copy.deepcopy(data['data_samples'])
            data_sample_data['data_manager_keys'] = [data_manager_key]
            self._register_data_sample(data_sample_data, dryrun)

        else:
            raise AssertionError(asset)
