import json
import ntpath

import os
import requests
import sys

from substra.utils import load_json_from_args
from .api import Api


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def load_data_files(data, attributes):
    files = {}
    exit_msg = {'message': []}
    exit = False

    for attribute in attributes:
        if attribute not in data:
            exit = True
            exit_msg['message'].append("The \'%s\' attribute has no file associated with it." % attribute)
        else:
            if os.path.exists(data[attribute]):
                files[attribute] = open(data[attribute], 'rb')
            else:
                exit = True
                exit_msg['message'].append("The \'%s\' attribute file (%s) does not exit." % (attribute, data[attribute]))

    return files, exit, exit_msg


class Add(Api):
    """Add asset"""

    def run(self):
        config = super(Add, self).run()

        asset = self.options['<asset>']
        args = self.options['<args>']
        dryrun = self.options.get('--dry-run', False)

        try:
            data = load_json_from_args(args)
        except Exception as e:
            self.handle_exception(e)

        exit = False

        files = {}
        if asset == 'dataset':
            files, exit, exit_msg = load_data_files(data, ['data_opener', 'description'])
        elif asset == 'challenge':
            files, exit, exit_msg = load_data_files(data, ['metrics', 'description'])
        elif asset == 'algo':
            files, exit, exit_msg = load_data_files(data, ['file', 'description'])
        elif asset == 'data':
            # support bulk with multiple files
            data_files = data.get('files', None)
            if data_files and type(data_files) == list:
                files = {
                    path_leaf(x): open(x, 'rb') for x in data_files
                }
            else:
                files, exit, exit_msg = load_data_files(data, ['file'])

        if exit:
            print(json.dumps(exit_msg))
            sys.exit(1)

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
