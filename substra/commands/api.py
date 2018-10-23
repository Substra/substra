import json

from .config import config_path
from .base import Base


class Api(Base):

    def run(self):

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            raise Exception('No config file found, please run "substra config <url> <version>"')
        else:
            return config



