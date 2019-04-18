import json

from substra_sdk_py import exceptions
from substra.utils import load_json_from_args

from .api import Api, DATA_SAMPLE_ASSET


class Register(Api):
    """Register asset"""

    ACCEPTED_ASSETS = [DATA_SAMPLE_ASSET]

    def run(self):
        super(Register, self).run()

        asset = self.get_asset_option()
        args = self.options['<args>']
        data = load_json_from_args(args)
        dryrun = self.options.get('--dry-run', False)

        try:
            res = self.client.register(asset, data, dryrun)
        except (exceptions.ConnectionError, exceptions.Timeout) as e:
            raise Exception(f'Failed to register {asset}: {e}')
        except exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content
            raise Exception(f'Failed to register {asset}: {e}: {error}')

        res = json.dumps(res, indent=2)
        print(res, end='')
        return res
