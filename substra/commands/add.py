import json
import ntpath

from substra_sdk_py import exceptions

from ..utils import load_json_from_args
from .. import assets
from .api import Api


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class Add(Api):
    """Add asset"""

    ACCEPTED_ASSETS = [
        assets.ALGO,
        assets.OBJECTIVE,
        assets.DATA_SAMPLE,
        assets.DATA_MANAGER,
        assets.TESTTUPLE,
        assets.TRAINTUPLE,
    ]
    ACCEPTED_REMOTE_ASSETS = [
        assets.DATA_SAMPLE,
    ]

    def run(self):
        super(Add, self).run()

        asset = self.get_asset_option()
        args = self.options['<args>']
        data = load_json_from_args(args)
        dryrun = self.options.get('--dry-run', False)

        remote = self.options.get('--remote', False)
        if remote and asset not in self.ACCEPTED_REMOTE_ASSETS:
            raise Exception(f"Cannot add remote asset {asset}")

        method = self.client.register if remote else self.client.add

        try:
            res = method(asset, data, dryrun)
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
