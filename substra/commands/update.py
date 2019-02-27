import json
import sys

import requests

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api


class Update(Api):
    """Update asset"""

    def run(self):
        config = super(Update, self).run()

        asset = self.options['<asset>']
        pkhash = self.options['<pkhash>']
        args = self.options['<args>']

        try:
            data = load_json_from_args(args)
        except InvalidJSONArgsException as e:
            self.handle_exception(e)
            sys.exit(1)

        kwargs = {}
        if config['auth']:
            kwargs.update({'auth': (config['user'], config['password'])})
        if config['insecure']:
            kwargs.update({'verify': False})
        try:
            r = requests.post('%s/%s/%s/update_ledger/' % (config['url'], asset, pkhash), data=data, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
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
