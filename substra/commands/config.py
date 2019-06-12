import copy
import json
import logging
import os

from .base import Base

from substra_sdk_py.config import default_config

config_path = os.path.expanduser('~/.substra')
logger = logging.getLogger(__name__)


class ConfigException(Exception):
    pass


def _read_config(path):
    with open(path) as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError:
            raise ConfigException(f"Cannot parse config file '{path}'")


def _write_config(path, config):
    with open(path, 'w') as fh:
        json.dump(config, fh, indent=2, sort_keys=True)


def load_profile(path, name):
    help_command = \
        "substra config <url> [<version>] [--profile=<profile>] [--config=<path>]"
    logger.debug(f"Loading profile '{name}' from '{path}'")

    try:
        config = _read_config(path)
    except FileNotFoundError:
        raise ConfigException(
            f"Config file '{path}' not found. Please run '{help_command}'.")
    try:
        return config[name]
    except KeyError:
        raise ConfigException(
            f"Config profile '{name}' not found. Please run '{help_command}'.")


def add_profile(path, name, profile):
    try:
        config = _read_config(path)
    except FileNotFoundError:
        config = copy.deepcopy(default_config)

    if name in config:
        config[name].update(profile)
    else:
        config[name] = profile
    _write_config(path, config)
    return config


class Config(Base):
    """Create config"""

    def run(self):
        """Add/modify profile to config file."""
        name = self.options.get('--profile', 'default')
        path = self.options.get('--config', config_path)

        profile = {
            'url': self.options['<url>'],
            'version': self.options.get('<version>', '0.0'),
            'insecure': self.options.get('--insecure',
                                         self.options.get('-k', False)),
            'auth': False,
        }

        user = self.options.get('<user>')
        password = self.options.get('<password>')

        if user and password:
            profile['auth'] = {
                'user': user,
                'password': password,
            }

        full_config = add_profile(path, name, profile)
        full_config_str = json.dumps(full_config, indent=2)
        print(f"Config from '{path}' has been updated with:\n{full_config_str}")
        return full_config
