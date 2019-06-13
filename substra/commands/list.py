import itertools
import json

from substra_sdk_py import exceptions

from .. import assets
from .api import Api

SIMPLE_ASSETS = [assets.TRAINTUPLE, assets.TESTTUPLE]


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


class List(Api):
    '''Get asset'''

    ACCEPTED_ASSETS = [
        assets.ALGO,
        assets.OBJECTIVE,
        assets.DATA_MANAGER,
        assets.MODEL,
        assets.TESTTUPLE,
        assets.TRAINTUPLE,
    ]

    def run(self):
        super(List, self).run()

        asset = self.get_asset_option()
        filters = self.options.get('<filters>', None)
        is_complex = self.options.get('--is-complex', False)

        try:
            res = self.client.list(asset, filters, is_complex)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to list {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to list {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
