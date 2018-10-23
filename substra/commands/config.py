import json
import os

from .base import Base

config_path = os.path.expanduser('~/.substra')

default_config = {
    'url': 'http://127.0.0.1:8000',
    'version': '0.0'
}


class Config(Base):
    """Create config"""

    def run(self):
        res = {}

        with open(config_path, 'a+') as f:
            try:
                res = json.load(f)
            except:
                # define default if does not exists
                res = default_config
            finally:
                res['url'] = self.options['<url>']
                res['version'] = self.options['<version>']
                f.seek(0)
                f.truncate()
                json.dump(res, f)
                return res
