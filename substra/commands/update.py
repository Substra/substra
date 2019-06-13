import json

from substra_sdk_py import exceptions

from .. import assets
from ..utils import load_json_from_args
from .api import Api


class Update(Api):
    """Update asset"""

    ACCEPTED_ASSETS = [
        assets.DATASET,
    ]

    def run(self):
        super(Update, self).run()

        asset = self.get_asset_option()
        asset = assets.to_server_name(asset)
        args = self.options['<args>']
        data = load_json_from_args(args)
        pkhash = self.options['<pkhash>']

        try:
            res = self.client.update(asset, pkhash, data)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to update {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to update {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
