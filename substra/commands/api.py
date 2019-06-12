from .config import config_path
from .config import load_profile
from .base import Base

from substra_sdk_py import Client

ALGO_ASSET = 'algo'
OBJECTIVE_ASSET = 'objective'
DATA_SAMPLE_ASSET = 'data_sample'
DATA_MANAGER_ASSET = 'data_manager'
DATASET_ASSET = 'dataset'
MODEL_ASSET = 'model'
TESTTUPLE_ASSET = 'testtuple'
TRAINTUPLE_ASSET = 'traintuple'

ALL_ASSETS = [ALGO_ASSET, OBJECTIVE_ASSET, DATA_SAMPLE_ASSET, DATA_MANAGER_ASSET, MODEL_ASSET, TESTTUPLE_ASSET, TRAINTUPLE_ASSET]


class InvalidAssetException(Exception):
    def __init__(self, accepted_assets, asset):
        if len(accepted_assets) > 1:
            accepted_assets = [f'"{accepted_asset}"' for accepted_asset in accepted_assets]
            accepted_assets = f'{", ".join(accepted_assets[:-1])} and {accepted_assets[-1]}'
            message = f'Invalid asset argument "{asset}", accepted values are {accepted_assets}'
        else:
            message = f'Invalid asset argument "{asset}", "{accepted_assets[0]}" is the only accepted value'
        super().__init__(message)


class Api(Base):
    ACCEPTED_ASSETS = ALL_ASSETS

    def run(self):
        # load config
        self.profile = self.options.get('--profile')
        self.profile = self.profile or 'default'
        path = self.options.get('--config')
        path = path or config_path
        config = load_profile(path, self.profile)

        # initialize substra client
        self.client = Client()
        self.client.create_config(profile=self.profile, **config)
        self.client.set_config(self.profile)

    def get_asset_option(self):
        asset = self.options['<asset>']
        if asset not in self.ACCEPTED_ASSETS:
            raise InvalidAssetException(self.ACCEPTED_ASSETS, asset)
        return asset
