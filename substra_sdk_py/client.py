from .get import get as getFunction
from .list import list as listFunction
from .add import add as addFunction
from .update import update as updateFunction
from .bulk_update import bulkUpdate as bulkUpdateFunction
from .path import path as pathFunction
from .config import ConfigManager


class Client(object):
    def __init__(self):

        self.configManager = ConfigManager()
        self.config = self.configManager.get('default')

    def create_config(self, profile, url='http://127.0.0.1:8000', version='0.0', user=None, password=None, insecure=False):
        return self.ConfigManager.create(profile=profile,
                                         url=url,
                                         version=version,
                                         user=user,
                                         password=password,
                                         insecure=insecure)

    def set_config(self, profile='default'):
        config = self.ConfigManager.get(profile)

        if isinstance(config, dict):
            self.config = config

        return config

    def get_config(self, profile='default'):
        return self.config

    def add(self, asset, data, dryrun=False):

        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return addFunction(asset, data, self.config, dryrun)

    def get(self, asset, pkhash):
        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return getFunction(asset, pkhash, self.config)

    def list(self, asset, filters=None, is_complex=False):
        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return listFunction(asset, self.config, filters, is_complex)

    def path(self, asset, pkhash, path):
        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return pathFunction(asset, pkhash, path, self.config)

    def update(self, asset, pkhash, data):
        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return updateFunction(asset, pkhash, data, self.config)

    def bulk_update(self, asset, args):
        if self.config is None:
            return 'Config is not set. Please create and set a config profile.'
        else:
            return bulkUpdateFunction(asset, args, self.config)
