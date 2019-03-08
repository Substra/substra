import json

import requests

from .api import Api, MODEL_ASSET, InvalidAssetException


class Path(Api):
    """Details asset"""

    ACCEPTED_ASSETS = [MODEL_ASSET]

    def run(self):
        config = super(Path, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            pkhash = self.options['<pkhash>']
            path = self.options['<path>']

            kwargs = {}
            if config['auth']:
                kwargs.update({'auth': (config['user'], config['password'])})
            if config['insecure']:
                kwargs.update({'verify': False})
            try:
                r = requests.get('%s/%s/%s/%s/' % (config['url'], asset, pkhash, path), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
            except:
                raise Exception('Failed to get path %s on %s' % (path, asset))
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
