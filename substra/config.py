import copy
import json
import logging
import os

from substra.sdk.config import default_config


logger = logging.getLogger(__name__)
config_path = os.path.expanduser('~/.substra')


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
    """Load profile from config path."""
    help_command = "substra config <url> ..."
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
    """Add profile to config path."""
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
