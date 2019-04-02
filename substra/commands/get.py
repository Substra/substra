import json

from substra_sdk_py import exceptions

from .api import Api, ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, \
    TRAINTUPLE_ASSET


class Get(Api):
    """Get asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

    def run(self):
        super(Get, self).run()

        asset = self.get_asset_option()
        pkhash = self.options['<pkhash>']

        try:
            res = self.client.get(asset, pkhash)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to get {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to get {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
