import json
import requests

from substra.utils import load_json_from_args
from .api import Api


class BulkUpdate(Api):
    """BulkUpdate asset"""

    def run(self):
        config = super(BulkUpdate, self).run()

        asset = self.options['<asset>']
        args = self.options['<args>']

        try:
            data = load_json_from_args(args)
        except Exception as e:
            self.handle_exception(e)

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.post('%s/%s/bulk_update/' % (config['url'], asset), data=data, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
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
