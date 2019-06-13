import json

from substra_sdk_py import exceptions
from substra.utils import load_json_from_args

from .. import assets
from .api import Api


class Register(Api):
    """Register asset"""

    ACCEPTED_ASSETS = [assets.DATA_SAMPLE,
                       assets.DATASET,
                       assets.OBJECTIVE]

    def _add_objective(self, data, dryrun):
        print('adding objective')
        asset = assets.OBJECTIVE
        # add objective, do not fail on conflict
        try:
            res = self.client.add(assets.OBJECTIVE, data, dryrun)
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
        asset = assets.DATA_MANAGER
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
        asset = assets.DATA_SAMPLE
        try:
            res = self.client.register(asset, data, dryrun)
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to create {asset}: {e}: {error}')

        print(json.dumps(res, indent=2), end='')
        if isinstance(res, list):
            return [r['pkhash'] for r in res]
        else:
            return res['pkhash']

    def run(self):
        super(Register, self).run()

        args = self.options['<args>']
        data = load_json_from_args(args)
        asset = self.get_asset_option()
        dryrun = self.options.get('--dry-run', False)

        if asset == assets.DATA_SAMPLE:
            self._register_data_sample(data, dryrun)

        elif asset == assets.DATASET:
            data_manager_data = data['data_manager']
            data_manager_key = self._add_data_manager(data_manager_data,
                                                      dryrun)

            data['data_samples']['data_manager_keys'] = [data_manager_key]
            self._register_data_sample(data['data_samples'], dryrun)

        elif asset == assets.OBJECTIVE:
            data_manager_key = self._add_data_manager(data['data_manager'],
                                                      dryrun)

            data['data_samples']['test_only'] = True
            data['data_samples']['data_manager_keys'] = [data_manager_key]
            data_sample_keys = self._register_data_sample(data['data_samples'],
                                                          dryrun)

            objective_data = data['objective']
            objective_data['test_data_manager_key'] = data_manager_key
            objective_data['test_data_sample_keys'] = data_sample_keys
            self._add_objective(objective_data, dryrun)

        else:
            raise AssertionError(asset)
