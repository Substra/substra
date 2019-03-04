import json

import requests
import itertools
from urllib.parse import quote
from .config import ConfigManager


SIMPLE_ASSETS = ['data', 'traintuple', 'testtuple']


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


def list(asset, filters=None, is_complex=False, profile='default'):
    configManager = ConfigManager()
    config = configManager.get(profile)

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

    url = '%s/%s/' % (config['url'], asset)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.get(url, headers=headers, **kwargs)
    except Exception as e:
        print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (asset, e))
    else:
        try:
            res = r.json()
        except:
            res = r.content
        else:
            res = flatten(res) if not is_complex and asset not in SIMPLE_ASSETS and r.status_code == 200 else res
        finally:
            return res
