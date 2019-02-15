import json
import requests

from .api import Api


class Update(Api):
    """BulkUpdate entity"""

    def run(self):
        config = super(Update, self).run()

        entity = self.options['<entity>']
        pkhash = self.options['<pkhash>']
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
            r = requests.post('%s/%s/%s/update_ledger/' % (config['url'], entity, pkhash), data=data, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
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
