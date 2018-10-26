import json

from .config import config_path
from .base import Base


class Api(Base):

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
        except Exception as e:
            msg = 'No config file or profile found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"'
            raise Exception(msg)
        else:
            return config
