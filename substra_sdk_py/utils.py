import itertools
import json
import contextlib
import os
from urllib.parse import quote

import ntpath


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def find_data_paths(data, attributes):
    paths = {}

    for attribute in attributes:
        if attribute not in data:
            raise LoadDataException(f"The '{attribute}' attribute is missing.")

        if not os.path.exists(data[attribute]):
            raise LoadDataException(f"The '{attribute}' attribute file ({data[attribute]}) does not exit.")

        paths[attribute] = data[attribute]

    return paths


@contextlib.contextmanager
def load_files(asset, data):
    paths = {}
    if asset == 'data_manager':
        paths = find_data_paths(data, ['data_opener', 'description'])
    elif asset == 'objective':
        paths = find_data_paths(data, ['metrics', 'description'])
    elif asset == 'algo':
        paths = find_data_paths(data, ['file', 'description'])
    elif asset == 'data_sample':
        data_paths = data.get('files', None)
        if data_paths and isinstance(data_paths, list):
            paths = {path_leaf(x): x for x in data_paths}
        else:
            paths = find_data_paths(data, ['file'])

    files = {k: open(f, 'rb') for k, f in paths.items()}

    try:
        yield files
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
