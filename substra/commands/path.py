import json

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
        except Exception:
            raise Exception('Failed to get path %s on %s' % (path, asset))

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
