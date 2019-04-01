import json

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
        except Exception:
            raise Exception('Failed to get %s' % asset)

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
