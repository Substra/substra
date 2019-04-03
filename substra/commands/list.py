import json

from substra_sdk_py import exceptions

import itertools

from .api import Api, ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TRAINTUPLE_ASSET, TESTTUPLE_ASSET

SIMPLE_ASSETS = [TRAINTUPLE_ASSET, TESTTUPLE_ASSET]


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


class List(Api):
    '''Get asset'''

    ACCEPTED_ASSETS = [ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

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
