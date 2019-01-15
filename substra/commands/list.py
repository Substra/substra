import json
from urllib.parse import urlencode, quote

import requests

from .api import Api


class List(Api):
    '''Get entity'''

    def run(self):
        config = super(List, self).run()

        base_url = config['url']
        entity = self.options['<entity>']
        filters = self.options.get('<filters>', None)

        url = base_url
        if filters:
            try:
                filters = json.loads(filters)
            except:
                res = 'Cannot load filters. Please review help substra -h'
                print(res)
                return res
            else:
                res = []
                for filter in filters:
                    if filter == 'OR':
                       filter = '-OR-'
                    res.append(quote(filter))

                get_parameters = quote(''.join(res))
                url = '%s?%s' % (url, get_parameters)

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.get('%s/%s/' % (url, entity), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except Exception as e:
            print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (entity, e))
        else:
            res = ''
            try:
                res = json.dumps(r.json(), indent=2)
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            finally:
                print(res, end='')
                return res
