import json

import requests
import itertools
from urllib.parse import quote

from .api import Api


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


class List(Api):
    '''Get entity'''

    def run(self):
        config = super(List, self).run()

        base_url = config['url']
        entity = self.options['<entity>']
        filters = self.options.get('<filters>', None)
        is_complex = self.options.get('--is-complex', False)
        url = base_url

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        if filters:
            try:
                filters = json.loads(filters)
            except:
                res = 'Cannot load filters. Please review help substra -h'
                print(res)
                return res
            else:
                filters = map(lambda x: '-OR-' if x == 'OR' else x, filters)
                # requests uses quote_plus to escape the params, but we want to use quote
                # we're therefore passing a string (won't be escaped again) instead of an object
                kwargs['params'] = 'search=%s' % quote(''.join(filters))

        try:
            r = requests.get('%s/%s/' % (url, entity), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except Exception as e:
            print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (entity, e))
        else:
            res = ''
            try:
                res = r.json()
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            else:
                res = flatten(res) if not is_complex else res
                res = json.dumps(res, indent=2)
            finally:
                print(res)
                return res
