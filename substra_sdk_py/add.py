import ntpath

import os
import requests


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def load_data_sample_files(data, attributes):
    files = {}

    for attribute in attributes:
        if attribute not in data:
            raise LoadDataException(f"The '{attribute}' attribute is missing.")
        else:
            if not os.path.exists(data[attribute]):
                raise LoadDataException(f"The '{attribute}' attribute file ({data[attribute]}) does not exit.")

            files[attribute] = open(data[attribute], 'rb')

    return files


def load_files(asset, data):
    files = {}
    if asset == 'data_manager':
        files = load_data_sample_files(data, ['data_opener', 'description'])
    elif asset == 'objective':
        files = load_data_sample_files(data, ['metrics', 'description'])
    elif asset == 'algo':
        files = load_data_sample_files(data, ['file', 'description'])
    elif asset == 'data_sample':
        # support bulk with multiple files
        # TODO add bulletproof for bulk using load_data_files
        data_files = data.get('files', None)
        if data_files and type(data_files) == list:
            files = {
                # open can fail
                path_leaf(x): open(x, 'rb') for x in data_files
            }
        else:
            files = load_data_sample_files(data, ['file'])

    return files


def add(asset, data, config, dryrun=False):
    # try loading files if needed
    files = load_files(asset, data)

    # build request
    if 'permissions' not in data:
        data['permissions'] = 'all'

    if dryrun:
        data['dryrun'] = True

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['user'], config['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/' % (config['url'], asset)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.post(url, data=data, files=files, headers=headers, **kwargs)
    except:
        raise Exception('Failed to create %s' % asset)
    else:
        res = ''
        try:
            result = r.json()
            res = {'result': result, 'status_code': r.status_code}
        except:
            res = r.content
        finally:
            return res
    finally:
        # close files
        if files:
            for x in files:
                files[x].close()
