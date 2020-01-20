import json
import os

from substra.sdk import exceptions

DEFAULT_PATH = os.path.expanduser('~/.substra-user')


def _read_user(path):
    with open(path) as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError:
            raise exceptions.UserException(f"Cannot parse user file '{path}'")


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

    def clear_user(self):
        try:
            os.remove(self.path)
        except OSError:  # file doesn't exist
            pass

    def load_user(self):
        """Load user from user file on disk.
        """
        return _read_user(self.path)

    def _write_user(self, path, user):
        with open(path, 'w') as fh:
            json.dump(user, fh, indent=2, sort_keys=True)
