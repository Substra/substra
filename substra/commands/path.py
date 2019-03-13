import json

from .api import Api, MODEL_ASSET, InvalidAssetException


class Path(Api):
    """Details asset"""

    ACCEPTED_ASSETS = [MODEL_ASSET]

    def run(self):
        super(Path, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            pkhash = self.options['<pkhash>']
            path = self.options['<path>']

            try:
                res = self.client.path(asset, pkhash, path)
            except:
                raise Exception('Failed to get path %s on %s' % (path, asset))
            else:
                try:
                    res = json.dumps(res, indent=2)
                except:
                    res = 'Can\'t decode response value from server to json: %s' % res
                finally:
                    print(res, end='')
                    return res
