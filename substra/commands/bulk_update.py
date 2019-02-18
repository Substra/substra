import json
import requests

from .api import Api


class BulkUpdate(Api):
    """BulkUpdate asset"""

    def run(self):
        config = super(BulkUpdate, self).run()

        asset = self.options['<asset>']
        args = self.options['<args>']

        try:
            data = json.loads(args)
        except:
            try:
                with open(args, 'r') as f:
                    data = json.load(f)
            except:
                raise Exception('Invalid args. Please review help')

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.post('%s/%s/bulk_update' % (config['url'], asset), data=data, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
        except:
            raise Exception('Failed to update')
        else:
            res = ''
            try:
                res = json.dumps(r.json())
            except:
                res = r.content
            finally:
                print(res, end='')
                return res
