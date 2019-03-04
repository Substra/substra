class ConfigManager(object):
    configs = {
        'default': {
            'url': 'http://127.0.0.1:8000',
            'version': '0.0',
            'auth': False,
            'insecure': False,
        }
    }

    def create(self, profile, url='http://127.0.0.1:8000', version='0.0', user=None, password=None, insecure=False):
        config = {
            'url': url,
            'version': version,
            'auth': False,
            'inscure': insecure
        }
        if user and password:
            config['auth'] = True
            config['user'] = user
            config['password'] = password

        # add to config list
        self.configs[profile] = config

        return config

    def get(self, profile):
        if profile in self.configs:
            return self.configs[profile]
        return f'{profile} config does not exist, please cretae it or use the default one.'
