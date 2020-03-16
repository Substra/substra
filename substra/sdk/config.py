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

logger = logging.getLogger(__name__)


class ConfigException(Exception):
    pass


class ProfileNotFoundError(ConfigException):
    pass


class _ProfileManager():
    DEFAULT_PATH = None

    def __init__(self, path=None, profiles=None):
        self.path = path or self.DEFAULT_PATH

        if self.path and os.path.exists(self.path):
            self.load_profiles()

        if profiles:
            self.profiles = profiles

        if not hasattr(self, 'profiles'):
            self.profiles = {}

    def load_profiles(self):
        with open(self.path) as fh:
            try:
                profiles = json.load(fh)
            except json.decoder.JSONDecodeError:
                raise ConfigException(f"Cannot parse config file '{self.path}'")
        self.profiles = profiles

    def save_profiles(self):
        with open(self.path, 'w') as f:
            json.dump(self.profiles, f, indent=2, sort_keys=True)

    def set_profile(self, profile_name, profile_data):
        self.profiles[profile_name] = profile_data

    def get_profile(self, profile_name):
        try:
            return self.profiles[profile_name]
        except KeyError:
            raise ProfileNotFoundError(profile_name)


class ProfileConfigManager(_ProfileManager):
    DEFAULT_PATH = os.path.expanduser('~/.substra')
    DEFAULT_VERSION = '0.0'
    DEFAULT_INSECURE = False

    def set_profile(self, profile_name, url, version=None, insecure=None):
        super().set_profile(profile_name, {
            'url': url,
            'version': version or self.DEFAULT_VERSION,
            'insecure': insecure or self.DEFAULT_INSECURE,
        })


class ProfileTokenManager(_ProfileManager):
    DEFAULT_PATH = os.path.expanduser('~/.substra-tokens')

    def set_profile(self, profile_name, token):
        super().set_profile(profile_name, {
            'token': token
        })
