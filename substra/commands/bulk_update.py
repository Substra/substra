import json

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
        except Exception:
            raise ValueError('Failed to bulk update %s' % asset)

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
