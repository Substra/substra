import json
from urllib.parse import quote

from .config import ConfigManager
from . import http_cli, helpers

SIMPLE_ASSETS = ['data_sample', 'traintuple', 'testtuple']


class Client(object):
    def __init__(self):
        # TODO make attributes private
        self.configManager = ConfigManager()
        self.config = self.configManager.get('default')

    def create_config(self, profile, url='http://127.0.0.1:8000',
                      version='0.0', auth=False, insecure=False):
        """Create new config profile."""
        return self.configManager.create(profile=profile,
                                         url=url,
                                         version=version,
                                         auth=auth,
                                         insecure=insecure)

    def set_config(self, profile='default'):
        """Set config profile."""
        self.config = self.configManager.get(profile)
        return self.config

    def get_config(self):
        """Get current config."""
        return self.config

    def _get_url(self, *parts):
        """Build url from config and list of strings."""
        url_parts = [self.config['url']]
        url_parts.extend(parts)
        url = '/'.join(url_parts)
        return url + '/'  # django requires a suffix /

    def add(self, asset, data, dryrun=False):
        """Add asset."""
        data = dict(data)  # make a copy for avoiding modification by reference
        if 'permissions' not in data:
            data['permissions'] = 'all'

        if dryrun:
            data['dryrun'] = True

        url = self._get_url(asset)

        with helpers.load_files(asset, data) as files:
            return http_cli.post(self.config, url, data, files=files)

    def get(self, asset, pkhash):
        """Get asset by key."""
        url = self._get_url(asset, pkhash)
        return http_cli.get(self.config, url)

    def list(self, asset, filters=None, is_complex=False):
        """List assets."""
        # TODO get rid of is_complex input args
        kwargs = {}
        if filters:
            try:
                filters = json.loads(filters)
            except ValueError:
                raise ValueError(
                    'Cannot load filters. Please review the documentation.')
            filters = map(lambda x: '-OR-' if x == 'OR' else x, filters)
            # requests uses quote_plus to escape the params, but we want to use
            # quote
            # we're therefore passing a string (won't be escaped again) instead
            # of an object
            kwargs['params'] = 'search=%s' % quote(''.join(filters))

        url = self._get_url(asset)
        result = http_cli.get(self.config, url, **kwargs)
        if not is_complex and asset not in SIMPLE_ASSETS:
            result = helpers.flatten(result)
        return result

    def path(self, asset, pkhash, path):
        """Get asset path."""
        url = self._get_url(asset, pkhash, path)
        return http_cli.get(self.config, url)

    def update(self, asset, pkhash, data):
        """Update asset by key."""
        url = self._get_url(asset, pkhash, 'update_ledger')
        return http_cli.post(self.config, url, data)

    def bulk_update(self, asset, data):
        """Update several assets."""
        url = self._get_url(asset, 'bulk_update')
        return http_cli.post(self.config, url, data)
