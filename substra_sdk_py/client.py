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

    def create_config(self, profile, url='http://127.0.0.1:8000',
                      version='0.0', auth=False, insecure=False):
        return self.configManager.create(profile=profile,
                                         url=url,
                                         version=version,
                                         auth=auth,
                                         insecure=insecure)

    def set_config(self, profile='default'):
        try:
            config = self.configManager.get(profile)
        except Exception as e:
            raise e
        else:
            self.config = config
            return config

    def get_config(self):
        return self.config

    def add(self, asset, data, dryrun=False):
        # make a copy for avoiding modification by reference
        data = dict(data)
        return addFunction(asset, data, self.config, dryrun)

    def get(self, asset, pkhash):
        return getFunction(asset, pkhash, self.config)

    def list(self, asset, filters=None, is_complex=False):
        return listFunction(asset, self.config, filters, is_complex)

    def path(self, asset, pkhash, path):
        return pathFunction(asset, pkhash, path, self.config)

    def update(self, asset, pkhash, data):
        # make a copy for avoiding modification by reference
        data = dict(data)
        return updateFunction(asset, pkhash, data, self.config)

    def bulk_update(self, asset, data):
        # make a copy for avoiding modification by reference
        data = dict(data)
        return bulkUpdateFunction(asset, data, self.config)
