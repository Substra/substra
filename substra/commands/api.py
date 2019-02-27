import json
import sys

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
        except FileNotFoundError as e:
            msg = 'No config file "%s" found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"' % conf_path
            print(msg)
            sys.exit(1)
        except KeyError as e:
            msg = 'No profile "%s" found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"' % profile
            print(msg)
            sys.exit(1)
        except Exception as e:
            msg = 'There is an issue with the config file loading, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"'
            raise Exception(msg)
        else:
            return config

    def handle_exception(self, exception):
        verbose = self.options.get('--verbose')
        if verbose:
            raise exception
        print(exception)
        sys.exit(1)
