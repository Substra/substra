import copy
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

        paths[attribute] = data[attribute]

    return paths


@contextlib.contextmanager
def extract_files(asset, data):
    data = copy.deepcopy(data)

    paths = {}
    if asset == 'data_manager':
        attributes = ['data_opener', 'description']
        paths = find_data_paths(data, attributes)
        [data.pop(x) for x in attributes]
    elif asset == 'objective':
        attributes = ['metrics', 'description']
        paths = find_data_paths(data, attributes)
        [data.pop(x) for x in attributes]
    elif asset == 'algo':
        attributes = ['file', 'description']
        paths = find_data_paths(data, attributes)
        [data.pop(x) for x in attributes]
    elif asset == 'data_sample':
        data_path = data.get('path', None)
        # support bulk with multiple files
        data_paths = data.get('paths', None)

        # validation
        if data_path and data_paths:
            raise Exception('Cannot use path and paths together.')

        if data_paths and isinstance(data_paths, list):
            for file_or_path in list(data_paths):
                # file case
                if os.path.isfile(file_or_path):
                    paths[path_leaf(file_or_path)] = file_or_path
                    data['paths'].remove(file_or_path)
        else:
            if os.path.isfile(data_path):
                paths = find_data_paths(data, ['path'])
                del data['path']

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
