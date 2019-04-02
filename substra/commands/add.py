import json
import ntpath

from substra_sdk_py import exceptions
from substra.utils import load_json_from_args
from .api import Api, ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, TRAINTUPLE_ASSET, TESTTUPLE_ASSET, \
    DATA_SAMPLE_ASSET


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class Add(Api):
    """Add asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, OBJECTIVE_ASSET, DATA_SAMPLE_ASSET, DATA_MANAGER_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

    def run(self):
        super(Add, self).run()

        asset = self.get_asset_option()
        args = self.options['<args>']
        data = load_json_from_args(args)
        dryrun = self.options.get('--dry-run', False)

        try:
            res = self.client.add(asset, data, dryrun)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to create {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to create {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
