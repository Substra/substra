import contextlib
import copy
import itertools
import functools
import json
import logging
import time
import os
from urllib.parse import quote

import ntpath

from . import assets


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


@contextlib.contextmanager
def extract_files(asset, data, extract_data_sample=True):
    data = copy.deepcopy(data)
    if asset == assets.DATASET:
        attributes = ['data_opener', 'description']
    elif asset == assets.OBJECTIVE:
        attributes = ['metrics', 'description']
    elif asset == assets.ALGO:
        attributes = ['file', 'description']
    else:
        attributes = []

    paths = {}
    for attr in attributes:
        try:
            paths[attr] = data[attr]
        except KeyError:
            raise LoadDataException(f"The '{attr}' attribute is missing.")
        del data[attr]

    # handle data sample specific case; paths and path cases
    if extract_data_sample and asset == 'data_sample':
        if data.get('path'):
            attr = 'path'
            paths[attr] = data[attr]
            del data[attr]

        for p in list(data.get('paths', [])):
            paths[path_leaf(p)] = p
            data['paths'].remove(p)

    files = {}
    for k, f in paths.items():
        if not os.path.exists(f):
            raise LoadDataException(f"The '{k}' attribute file ({f}) does not exit.")
        files[k] = open(f, 'rb')

    try:
        yield (data, files)
    finally:
        for f in files.values():
            f.close()


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


def parse_filters(filters):
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
    return 'search=%s' % quote(''.join(filters))


def retry_on_exception(exceptions, timeout=False):
    """Retry function in case of exception(s)."""
    def _retry(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            delay = 1
            backoff = 2
            tstart = time.time()

            while True:
                try:
                    return f(*args, **kwargs)

                except exceptions:
                    if timeout is not False and time.time() - tstart > timeout:
                        raise
                    logging.warning(
                        f'Function {f.__name__} failed: retrying in {delay}s')
                    time.sleep(delay)
                    delay *= backoff

        return wrapper
    return _retry
