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

import json
import logging
import os
from copy import copy

logger = logging.getLogger(__name__)


class ConfigException(Exception):
    pass


class ProfileNotFoundError(ConfigException):
    pass


class ConfigManager():
    DEFAULT_CONFIG_PATH = os.path.expanduser('~/.substra')
    DEFAULT_TOKENS_PATH = os.path.expanduser('~/.substra-tokens')
    DEFAULT_VERSION = '0.0'
    DEFAULT_INSECURE = False

    def __init__(self, config_path=None, tokens_path=None):
        self._config_path = str(config_path) or self.DEFAULT_CONFIG_PATH
        config_tokens_path, profiles = self._load_config()

        self._tokens_path = tokens_path or config_tokens_path or self.DEFAULT_TOKENS_PATH
        tokens = self._load_tokens()

        self._profiles = profiles
        self._tokens = tokens

    def _load_config(self):
        tokens_path = None
        profiles = {}

        if not os.path.exists(self._config_path):
            return tokens_path, profiles

        with open(self._config_path) as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                raise ConfigException(f"Cannot parse config file '{self._config_path}'")

        profiles = data.get('profiles', profiles)
        tokens_path = data.get('tokens_path', tokens_path)

        return tokens_path, profiles

    def _load_tokens(self):
        tokens = {}

        if not os.path.exists(self._tokens_path):
            return tokens

        with open(self._tokens_path) as f:
            try:
                tokens = json.load(f)
            except json.decoder.JSONDecodeError:
                raise ConfigException(f"Cannot parse tokens file '{self._tokens_path}'")

        return tokens

    def save(self):
        self._save_config()
        self._save_tokens()

    def _save_config(self):
        with open(self._config_path, 'w') as f:
            json.dump({
                'tokens_path': self._tokens_path,
                'profiles': self._profiles,
            }, f, indent=2, sort_keys=True)

    def _save_tokens(self):
        with open(self._tokens_path, 'w') as f:
            json.dump(self._tokens, f, indent=2, sort_keys=True)

    def set_profile(self, profile_name, url, version=None, insecure=None, token=None):
        self._profiles[profile_name] = {
            'url': url,
            'version': version or self.DEFAULT_VERSION,
            'insecure': insecure or self.DEFAULT_INSECURE,
        }

        if token:
            self.set_token(profile_name, token)

    def set_token(self, profile_name, token):
        self._tokens[profile_name] = token

    def get_profile(self, profile_name):
        if profile_name not in self._profiles:
            raise ProfileNotFoundError(f'Profile not found: {profile_name}')

        profile = copy(self._profiles[profile_name])

        if profile_name in self._tokens:
            profile['token'] = self._tokens[profile_name]

        return profile
