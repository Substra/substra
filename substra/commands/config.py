import json
import os

from .base import Base

# default, you can override it with --config <configuration_file_path>
config_path = os.path.expanduser('~/.substra')

default_config = {
    'default': {
        'url': 'http://127.0.0.1:8000',
        'version': '0.0'
    }
}

class Config(Base):
    """Create config"""

    def run(self):
        res = {}

        # check overrides
        profile = self.options.get('--profile')
        if not profile:
            profile = 'default'

        conf_path = self.options.get('--config')
        if not conf_path:
            conf_path = config_path

        with open(conf_path, 'a+') as f:
            try:
                f.seek(0)
                res = json.load(f)
            except Exception as e:
                # define default if does not exists
                res = default_config
            finally:
                if profile not in res:
                    res[profile] = {}

                res[profile]['url'] = self.options['<url>']
                res[profile]['version'] = self.options.get('<version>', '0.0')
                user = self.options.get('<user>', None)
                pwd = self.options.get('<pass>', None)
                if user and pwd:
                    res[profile]['auth'] = True
                    res[profile]['user'] = user
                    res[profile]['pass'] = pwd
                else:
                    res[profile]['auth'] = False

                f.seek(0)
                f.truncate()
                json.dump(res, f)

                print('Created/Updated config file in %s with values: %s' % (conf_path, json.dumps(res, indent=2)))

                return res
