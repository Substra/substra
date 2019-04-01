import json

from substra_sdk_py import exceptions

from substra.utils import load_json_from_args
from .api import Api, DATA_MANAGER_ASSET


class Update(Api):
    """Update asset"""

    ACCEPTED_ASSETS = [DATA_MANAGER_ASSET]

    def run(self):
        super(Update, self).run()

        asset = self.get_asset_option()
        args = self.options['<args>']
        data = load_json_from_args(args)
        pkhash = self.options['<pkhash>']

        try:
            res = self.client.update(asset, pkhash, data)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to update {asset}: {e}')
        except exceptions.HTTPError as e:
            error = e.response.json()
            raise Exception(f'Failed to update {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
