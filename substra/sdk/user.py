import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_PATH = os.path.expanduser('~/.substra-user')


class UserException(Exception):
    pass


def _read_user(path):
    with open(path) as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError:
            raise UserException(f"Cannot parse user file '{path}'")


class Manager():
    def __init__(self, path=DEFAULT_PATH):
        self.path = path

    def add_user(self, token):
        # create profile
        user = {
            'token': token,
        }

        self._write_user(self.path, user)
        return user

    def load_user(self):
        """Load user from user file on disk.
        """
        logger.debug(f"Loading user from '{self.path}'")
        return _read_user(self.path)

    def _write_user(self, path, user):
        with open(path, 'w') as fh:
            json.dump(user, fh, indent=2, sort_keys=True)
