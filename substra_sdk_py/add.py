import contextlib
import os

import ntpath
import requests


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
        # support bulk with multiple paths
        # TODO add bulletproof for bulk using load_data_paths
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


def add(asset, data, config, dryrun=False):
    # build request
    if 'permissions' not in data:
        data['permissions'] = 'all'

    if dryrun:
        data['dryrun'] = True

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['auth']['user'], config['auth']['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/' % (config['url'], asset)
    headers = {'Accept': 'application/json;version=%s' % config['version']}

    with load_files(asset, data) as files:
        try:
            r = requests.post(url, data=data, files=files, headers=headers,
                              **kwargs)
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise

        try:
            result = r.json()
        except ValueError:
            raise

        return result
