import json

import requests

from .api import Api


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
            files = {
                'file': open(data['file'], 'rb'),
            }

        try:
            r = requests.post('%s/%s/' % (config['url'], entity), files=files, data=data, headers={'Accept': 'application/json;version=%s' % config['version']})
        except:
            raise Exception('Failed to create %s' % entity)
        else:
            res = json.dumps(r.json())
            print(res, end='')
            return res
