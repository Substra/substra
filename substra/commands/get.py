import json

import requests

from .api import Api, ALGO_ASSET, CHALLENGE_ASSET, DATASET_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, \
    TRAINTUPLE_ASSET, InvalidAssetException


class Get(Api):
    """Get asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, CHALLENGE_ASSET, DATASET_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

    def run(self):
        config = super(Get, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
            return
        pkhash = self.options['<pkhash>']

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.get('%s/%s/%s/' % (config['url'], asset, pkhash), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except:
            raise Exception('Failed to get %s' % asset)
        else:
            res = ''
            try:
                result = r.json()
                res = json.dumps({'result': result, 'status_code': r.status_code}, indent=2)
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            finally:
                print(res, end='')
                return res
