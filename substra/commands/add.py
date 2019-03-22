import json
import ntpath

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api, ALGO_ASSET, CHALLENGE_ASSET, DATA_MANAGER_ASSET, TRAINTUPLE_ASSET, TESTTUPLE_ASSET, \
    DATA_SAMPLE_ASSET, InvalidAssetException


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class Add(Api):
    """Add asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, CHALLENGE_ASSET, DATA_SAMPLE_ASSET, DATA_MANAGER_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

    def run(self):
        super(Add, self).run()

        try:
            asset = self.get_asset_option()
        except InvalidAssetException as e:
            self.handle_exception(e)
        else:
            args = self.options['<args>']
            dryrun = self.options.get('--dry-run', False)

            try:
                data = load_json_from_args(args)
            except InvalidJSONArgsException as e:
                self.handle_exception(e)
            else:
                try:
                    res = self.client.add(asset, data, dryrun)
                except:
                    raise Exception('Failed to create %s' % asset)
                else:
                    try:
                        res = json.dumps(res, indent=2)
                    except:
                        res = 'Can\'t decode response value from server to json: %s' % res
                    finally:
                        print(res, end='')
                        return res
