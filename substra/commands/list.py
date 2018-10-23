import json

import requests

from .api import Api


class List(Api):
    """Get entity"""

    def run(self):
        config = super(List, self).run()

        base_url = config['url']
        entity = self.options['<entity>']
        filters = self.options.get('<filters>', None)

        url = base_url
        # TODO handle filtering
        if filters:
            pass

        try:
            r = requests.get('%s/%s/' % (url, entity), headers={'Accept': 'application/json;version=%s' % config['version']})
        except:
            raise Exception('Failed to list %s' % entity)
        else:
            try:
                res = json.dumps(r.json())
            except:
                msg = 'Can\'t decode response value to json. Please make sure the substrabac instance is live.'
                print(msg)
                return msg
            else:
                print(res, end='')
                return res
