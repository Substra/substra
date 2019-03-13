import copy

default_config = {
    'default': {
        'url': 'http://127.0.0.1:8000',
        'version': '0.0',
        'auth': False,
        'insecure': False,
    }
}


class ConfigManager(object):
    config = copy.deepcopy(default_config)

    def create(self, profile, url='http://127.0.0.1:8000', version='0.0',
               auth=False, insecure=False):

        config = {
            'url': url,
            'version': version,
            'auth': auth,
            'insecure': insecure
        }

        # add to config list
        self.config[profile] = config

        return config

    def get(self, profile):
        if profile in self.config:
            return self.config[profile]
        raise Exception(f'{profile} config does not exist, please create it or use the default one.')
