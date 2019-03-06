import json
import sys

from .config import config_path
from .base import Base

ALGO_ASSET = 'algo'
CHALLENGE_ASSET = 'challenge'
DATA_ASSET = 'data'
DATASET_ASSET = 'dataset'
MODEL_ASSET = 'model'
TESTTUPLE_ASSET = 'testtuple'
TRAINTUPLE_ASSET = 'traintuple'

ALL_ASSETS = [ALGO_ASSET, CHALLENGE_ASSET, DATA_ASSET, DATASET_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]


class InvalidAssetException(Exception):
    def __init__(self, accepted_assets, asset):
        accepted_assets = [f'"{accepted_asset}"' for accepted_asset in accepted_assets]
        if len(accepted_assets) > 1:
            accepted_assets = ', '.join(accepted_assets[:-1]) + ' and ' + accepted_assets[-1]
        else:
            accepted_assets = accepted_assets[0]
        super().__init__(f'Invalid asset argument "{asset}", accepted values are {accepted_assets}')


class Api(Base):
    ACCEPTED_ASSETS = ALL_ASSETS[:]

    def run(self):

        # check overrides
        profile = self.options.get('--profile')
        if not profile:
            profile = 'default'

        conf_path = self.options.get('--config')
        if not conf_path:
            conf_path = config_path

        try:
            with open(conf_path, 'r') as f:
                config = json.load(f)[profile]
        except FileNotFoundError as e:
            msg = 'No config file "%s" found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"' % conf_path
            print(msg)
            sys.exit(1)
        except KeyError as e:
            msg = 'No profile "%s" found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"' % profile
            print(msg)
            sys.exit(1)
        except Exception as e:
            msg = 'There is an issue with the config file loading, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"'
            raise Exception(msg)
        else:
            return config

    def handle_exception(self, exception):
        verbose = self.options.get('--verbose', False)
        if verbose:
            raise exception
        print(str(exception))

    def get_asset_option(self):
        asset = self.options['<asset>']
        if asset not in self.ACCEPTED_ASSETS:
            raise InvalidAssetException(self.ACCEPTED_ASSETS, asset)
        return asset
