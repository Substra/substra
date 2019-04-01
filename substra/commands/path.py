import json

from substra_sdk_py import exceptions

from .api import Api, MODEL_ASSET


class Path(Api):
    """Details asset"""

    ACCEPTED_ASSETS = [MODEL_ASSET]

    def run(self):
        super(Path, self).run()

        asset = self.get_asset_option()
        pkhash = self.options['<pkhash>']
        path = self.options['<path>']

        try:
            res = self.client.path(asset, pkhash, path)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to get path {asset}: {e}')
        except exceptions.HTTPError as e:
            error = e.response.json()
            raise Exception(f'Failed to get path {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
