import json

from substra_sdk_py import exceptions

from substra.utils import load_json_from_args
from .api import Api, DATA_SAMPLE_ASSET


class BulkUpdate(Api):
    """BulkUpdate asset"""

    ACCEPTED_ASSETS = [DATA_SAMPLE_ASSET]

    def run(self):
        super(BulkUpdate, self).run()

        asset = self.get_asset_option()
        args = self.options['<args>']
        data = load_json_from_args(args)

        try:
            res = self.client.bulk_update(asset, data)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to bulk update {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to bulk update {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
