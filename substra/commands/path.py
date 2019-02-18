import json

import requests

from .api import Api


class Path(Api):
    """Details asset"""

    def run(self):
        config = super(Path, self).run()

        asset = self.options['<asset>']
        pkhash = self.options['<pkhash>']
        path = self.options['<path>']

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.get('%s/%s/%s/%s' % (config['url'], asset, pkhash, path), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except:
            raise Exception('Failed to get %s' % asset)
        else:
            res = ''
            try:
                res = json.dumps(r.json(), indent=2)
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            finally:
                print(res, end='')
                return res
