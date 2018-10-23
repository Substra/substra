import json

import requests

from .api import Api


class Get(Api):
    """Get entity"""

    def run(self):
        config = super(Get, self).run()

        entity = self.options['<entity>']
        pkhash = self.options['<pkhash>']

        try:
            r = requests.get('%s/%s/%s' % (config['url'], entity, pkhash), headers={'Accept': 'application/json;version=%s' % config['version']})
        except:
            raise Exception('Failed to get %s' % entity)
        else:
            res = json.dumps(r.json())
            print(res, end='')
            return res
