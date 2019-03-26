import json

import itertools

from .api import Api, ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TRAINTUPLE_ASSET, TESTTUPLE_ASSET, \
    InvalidAssetException

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

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            filters = self.options.get('<filters>', None)
            is_complex = self.options.get('--is-complex', False)

            try:
                res = self.client.list(asset, filters, is_complex)
            except Exception as e:
                print('Failed to list %s. Please make sure the substrabac instance is live. Detail %s' % (asset, e))
            else:
                try:
                    res = json.dumps(res, indent=2)
                except:
                    res = 'Can\'t decode response value from server to json: %s' % res
                finally:
                    print(res, end='')
                    return res
