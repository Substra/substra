# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_PATH = os.path.expanduser('~/.substra')
DEFAULT_VERSION = '0.0'
DEFAULT_URL = 'http://127.0.0.1:8000'
DEFAULT_PROFILE_NAME = 'default'
DEFAULT_INSECURE = False

DEFAULT_CONFIG = {
    DEFAULT_PROFILE_NAME: {
        'url': DEFAULT_URL,
        'version': DEFAULT_VERSION,
        'insecure': DEFAULT_INSECURE,
    }
}


class ConfigException(Exception):
    pass


class ProfileNotFoundError(ConfigException):
    pass


def _read_config(path):
    if not os.path.exists(path):
        raise ConfigException(f"Cannot find config file '{path}'")

    with open(path) as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError:
            raise ConfigException(f"Cannot parse config file '{path}'")


def _write_config(path, config):
    with open(path, 'w') as fh:
        json.dump(config, fh, indent=2, sort_keys=True)


def create_profile(url, version, insecure):
    """Create profile object."""
    return {
        'url': url,
        'version': version,
        'insecure': insecure,
    }


def _add_profile(path, name, url, version, insecure):
    """Add profile to config file on disk."""
    # read config file
    try:
        config = _read_config(path)
    except ConfigException:
        config = copy.deepcopy(DEFAULT_CONFIG)

    # create profile
    profile = create_profile(url, version, insecure)

    # update config file
    if name in config:
        config[name].update(profile)
    else:
        config[name] = profile

    _write_config(path, config)
    return config


def _from_config_file(path, name):
    """Load profile from config file on disk.

    Raises:
        FileNotFoundError: if config file does not exist.
        ProfileNotFoundError: if profile does not exist.
    """
    logger.debug(f"Loading profile '{name}' from '{path}'")
    try:
        config = _read_config(path)
    except ConfigException:
        config = copy.deepcopy(DEFAULT_CONFIG)

    try:
        return config[name]
    except KeyError:
        raise ProfileNotFoundError(name)


class Manager:
    def __init__(self, path=DEFAULT_PATH):
        self.path = path

    def add_profile(
        self, name, url=DEFAULT_URL, version=DEFAULT_VERSION, insecure=False
    ):
        """Add profile to config file on disk."""
        config = _add_profile(self.path, name, url, version=version, insecure=insecure,)
        return config[name]

    def from_config_file(self, name=DEFAULT_PROFILE_NAME):
        """Load profile from config file on disk.

        Raises:
            FileNotFoundError: if config file does not exist.
            ProfileNotFoundError: if profile does not exist.
        """
        return _from_config_file(self.path, name)
