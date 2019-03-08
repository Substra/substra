import json
import sys

import requests

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api, DATA_ASSET, InvalidAssetException


class BulkUpdate(Api):
    """BulkUpdate asset"""

    ACCEPTED_ASSETS = [DATA_ASSET]

    def run(self):
        config = super(BulkUpdate, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
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
                r = requests.post('%s/%s/bulk_update/' % (config['url'], asset), data=data, headers={'Accept': 'application/json;version=%s' % config['version']}, **kwargs)
            except:
                raise Exception('Failed to bulk update %s' % asset)
            else:
                res = ''
                try:
                    result = r.json()
                    res = json.dumps({'result': result, 'status_code': r.status_code}, indent=2)
                except:
                    res = r.content
                finally:
                    print(res, end='')
                    return res
