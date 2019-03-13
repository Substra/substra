import json

from .api import Api, ALGO_ASSET, CHALLENGE_ASSET, DATASET_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, \
    TRAINTUPLE_ASSET, InvalidAssetException


class Get(Api):
    """Get asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, CHALLENGE_ASSET, DATASET_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

    def run(self):
        super(Get, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            pkhash = self.options['<pkhash>']

            try:
                res = self.client.get(asset, pkhash)
            except:
                raise Exception('Failed to get %s' % asset)
            else:
                try:
                    res = json.dumps(res, indent=2)
                except:
                    res = 'Can\'t decode response value from server to json: %s' % res
                finally:
                    print(res, end='')
                    return res
