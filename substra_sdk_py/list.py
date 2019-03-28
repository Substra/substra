import json

import requests
import itertools
from urllib.parse import quote

from .config import requests_get_params


SIMPLE_ASSETS = ['data_sample', 'traintuple', 'testtuple']


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


def list(asset, config, filters=None, is_complex=False):

    kwargs, headers = requests_get_params(config)

    if filters:
        try:
            filters = json.loads(filters)
        except:
            res = 'Cannot load filters. Please review the documentation.'
            print(res)
            return res
        else:
            filters = map(lambda x: '-OR-' if x == 'OR' else x, filters)
            # requests uses quote_plus to escape the params, but we want to use quote
            # we're therefore passing a string (won't be escaped again) instead of an object
            kwargs['params'] = 'search=%s' % quote(''.join(filters))

    url = '%s/%s/' % (config['url'], asset)
    try:
        r = requests.get(url, headers=headers, **kwargs)
    except Exception as e:
        print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (asset, e))
    else:
        res = ''
        try:
            result = r.json()
            result = flatten(result) if not is_complex and asset not in SIMPLE_ASSETS and r.status_code == 200 else result
            res = {'result': result, 'status_code': r.status_code}
        except:
            res = r.content
        finally:
            return res
