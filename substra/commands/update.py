import json

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api, DATA_MANAGER_ASSET, InvalidAssetException


class Update(Api):
    """Update asset"""

    ACCEPTED_ASSETS = [DATA_MANAGER_ASSET]

    def run(self):
        super(Update, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            pkhash = self.options['<pkhash>']
            args = self.options['<args>']

            try:
                data = load_json_from_args(args)
            except InvalidJSONArgsException as e:
                self.handle_exception(e)
            else:
                try:
                    res = self.client.update(asset, pkhash, data)
                except:
                    raise Exception('Failed to update %s' % asset)
                else:
                    try:
                        res = json.dumps(res, indent=2)
                    except:
                        res = 'Can\'t decode response value from server to json: %s' % res
                    finally:
                        print(res, end='')
                        return res
