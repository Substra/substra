import copy
import json
import os

from .base import Base

from substra_sdk_py.config import default_config

# default, you can override it with --config <configuration_file_path>
config_path = os.path.expanduser('~/.substra')


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
            except:
                # define default if does not exists
                res = copy.deepcopy(default_config)
            finally:
                if profile not in res:
                    res[profile] = {}

                res[profile]['url'] = self.options['<url>']
                res[profile]['version'] = self.options.get('<version>', '0.0')
                res[profile]['insecure'] = self.options.get('--insecure', self.options.get('-k', False))
                user = self.options.get('<user>', None)
                password = self.options.get('<password>', None)

                res[profile]['auth'] = False
                if user and password:
                    res[profile]['auth'] = {
                        'user': user,
                        'password': password
                    }

                f.seek(0)
                f.truncate()
                json.dump(res, f, indent=2, sort_keys=True)

                print('Created/Updated config file in %s with values: \n%s' % (conf_path, json.dumps(res, indent=2)))

                return res
