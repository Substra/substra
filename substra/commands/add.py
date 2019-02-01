import json
import ntpath

import requests

from .api import Api

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class Add(Api):
    """Add entity"""

    def run(self):
        config = super(Add, self).run()

        entity = self.options['<entity>']
        args = self.options['<args>']

        try:
            data = json.loads(args)
        except:
            try:
                with open(args, 'r') as f:
                    data = json.load(f)
            except:
                raise Exception('Invalid args. Please review help')

        # TODO add try except on this part of the code
        files = {}
        if entity == 'dataset':
            files = {
                'data_opener': open(data['data_opener'], 'rb'),
                'description': open(data['description'], 'rb')
            }
        elif entity == 'challenge':
            files = {
                'metrics': open(data['metrics'], 'rb'),
                'description': open(data['description'], 'rb')
            }
        elif entity == 'algo':
            files = {
                'file': open(data['file'], 'rb'),
                'description': open(data['description'], 'rb')
            }
        elif entity == 'data':
            # support bulk with multiple files
            files = data.get('files', None)
            if files and type(files) == list:
                files = {
                    path_leaf(x): open(x, 'rb') for x in files
                }
            else:
                files = {
                    'file': open(data['file'], 'rb'),
                }

        if 'permissions' not in data:
            data['permissions'] = 'all'

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.post('%s/%s/' % (config['url'], entity), data=data, files=files, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except:
            raise Exception('Failed to create %s' % entity)
        else:
            res = ''
            try:
                res = json.dumps(r.json(), indent=2)
            except:
                res = r.content
            finally:
                print(res)
                return res
