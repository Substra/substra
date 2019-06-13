import json

from substra_sdk_py import exceptions

from .. import assets
from .api import Api


class Get(Api):
    """Get asset"""

    ACCEPTED_ASSETS = [
        assets.ALGO,
        assets.OBJECTIVE,
        assets.DATA_MANAGER,
        assets.MODEL,
        assets.TESTTUPLE,
        assets.TRAINTUPLE,
    ]

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
