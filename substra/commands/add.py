import json
import ntpath

import os

from substra.utils import load_json_from_args, InvalidJSONArgsException
from .api import Api, ALGO_ASSET, CHALLENGE_ASSET, DATASET_ASSET, TRAINTUPLE_ASSET, TESTTUPLE_ASSET, \
    DATA_ASSET, InvalidAssetException


class LoadDataException(Exception):
    pass


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def load_data_files(data, attributes):
    files = {}

    for attribute in attributes:
        if attribute not in data:
            raise LoadDataException(f"The '{attribute}' attribute is missing.")
        else:
            if not os.path.exists(data[attribute]):
                raise LoadDataException(f"The '{attribute}' attribute file ({data[attribute]}) does not exit.")

            files[attribute] = open(data[attribute], 'rb')

    return files


class Add(Api):
    """Add asset"""

    ACCEPTED_ASSETS = [ALGO_ASSET, CHALLENGE_ASSET, DATA_ASSET, DATASET_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]

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
