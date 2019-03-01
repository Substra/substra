import json
import ntpath

import os
import requests

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def load_data_files(data, attributes):
    files = {}

    for attribute in attributes:
        if attribute not in data:
            raise LoadDataException(f"The '{attribute}' attribute is missing.")
        else:
            if not os.path.exists(data[attribute]):
                raise LoadDataException(f"The '{attribute}' attribute file ({data[attribute]}) does not exit.")

            files[attribute] = open(data[attribute], 'rb')

    return files


class Add(Api):
    """Add asset"""

    def load_files(self, asset, data):
        files = {}
        if asset == 'dataset':
            files = load_data_files(data, ['data_opener', 'description'])
        elif asset == 'challenge':
            files = load_data_files(data, ['metrics', 'description'])
        elif asset == 'algo':
            files = load_data_files(data, ['file', 'description'])
        elif asset == 'data':
            # support bulk with multiple files
            # TODO add bulletproof for bulk using load_data_files
            data_files = data.get('files', None)
            if data_files and type(data_files) == list:
                files = {
                    # open can fail
                    path_leaf(x): open(x, 'rb') for x in data_files
                }
            else:
                files = load_data_files(data, ['file'])

        return files

    def run(self):
        config = super(Add, self).run()

        asset = self.options['<asset>']
        args = self.options['<args>']
        dryrun = self.options.get('--dry-run', False)

        try:
            data = load_json_from_args(args)
        except InvalidJSONArgsException as e:
            self.handle_exception(e)
        else:
            try:
                # try loading files if needed
                files = self.load_files(asset, data)
            except Exception as e:
                self.handle_exception(e)
            else:
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
                try:
                    r = requests.post('%s/%s/' % (config['url'], asset), data=data, files=files, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
                except:
                    raise Exception('Failed to create %s' % asset)
                else:
                    res = ''
                    try:
                        res = json.dumps(r.json(), indent=2)
                    except:
                        res = r.content
                    finally:
                        print(res)
                        return res
