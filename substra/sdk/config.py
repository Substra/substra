import abc
import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_PATH = "~/.substra"
DEFAULT_TOKENS_PATH = "~/.substra-tokens"
DEFAULT_PROFILE_NAME = "default"
DEFAULT_INSECURE = False


class ConfigException(Exception):
    pass


class ProfileNotFoundError(ConfigException):
    pass


class _ProfileManager(abc.ABC):
    def __init__(self, path):
        self._path = path
        self._profiles = self.load()

    def load(self):
        if not os.path.exists(self._path):
            return {}

        with open(self._path) as fh:
            try:
                self._profiles = json.load(fh)
            except json.decoder.JSONDecodeError:
                raise ConfigException(f"Cannot parse config file '{self._path}'")

        return self._profiles

    def save(self):
        with open(self._path, "w") as fh:
            json.dump(self._profiles, fh, indent=2, sort_keys=True)

    def get_profile(self, name):
        try:
            return self._profiles[name]
        except KeyError:
            raise ProfileNotFoundError(name)

    def set_profile(self, name, profile):
        if name in self._profiles:
            self._profiles[name].update(profile)
        else:
            self._profiles[name] = profile
        return self._profiles[name]


class ConfigManager(_ProfileManager):
    def set_profile(self, name, url, insecure=False):
        return super().set_profile(
            name,
            {
                "url": url,
                "insecure": insecure,
            },
        )


class TokenManager(_ProfileManager):
    def set_profile(self, name, token):
        return super().set_profile(
            name,
            {
                "token": token,
            },
        )

    def get_profile(self, name):
        profile = super().get_profile(name)
        return profile["token"]
