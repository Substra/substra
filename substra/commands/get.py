import json

import requests

from .api import Api


class Get(Api):
    """Get entity"""

    def run(self):
        config = super(Get, self).run()

        entity = self.options['<entity>']
        pkhash = self.options['<pkhash>']

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.get('%s/%s/%s' % (config['url'], entity, pkhash), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except:
            raise Exception('Failed to get %s' % entity)
        else:
            res = ''
            try:
                res = json.dumps(r.json())
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            finally:
                print(res, end='')
                return res
