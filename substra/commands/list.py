import json

import requests

from .api import Api


def flatten(list_of_list):
    res = []
    for l in list_of_list:
        for item in l:
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
                kwargs['params'] = {'search': ''.join(filters)}

        try:
            r = requests.get('%s/%s/' % (url, entity), headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except Exception as e:
            print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (entity, e))
        else:
            res = ''
            try:
                res = r.json()
                res = flatten(res)
                res = json.dumps(res, indent=2)
            except:
                res = 'Can\'t decode response value from server to json: %s' % r.content
            finally:
                print(res)
                return res
