import json

import requests
import itertools
from urllib.parse import quote

from . import http_cli


SIMPLE_ASSETS = ['data_sample', 'traintuple', 'testtuple']


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


def list(asset, config, filters=None, is_complex=False):
    kwargs = {}
    if filters:
        try:
            filters = json.loads(filters)
        except ValueError:
            raise ValueError(
                'Cannot load filters. Please review the documentation.')
        filters = map(lambda x: '-OR-' if x == 'OR' else x, filters)
        # requests uses quote_plus to escape the params, but we want to use
        # quote
        # we're therefore passing a string (won't be escaped again) instead
        # of an object
        kwargs['params'] = 'search=%s' % quote(''.join(filters))

    url = '%s/%s/' % (config['url'], asset)
    result = http_cli.get(config, url, **kwargs)
    if not is_complex and asset not in SIMPLE_ASSETS:
        result = flatten(result)
    return result
