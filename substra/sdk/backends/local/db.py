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

import collections
import logging

from substra.sdk import exceptions

logger = logging.getLogger(__name__)


class InMemoryDb:
    """In memory data db."""

    def __init__(self):
        # assets stored per type and per key
        self._data = collections.defaultdict(dict)

    def add(self, asset):
        """Add an asset."""
        type_ = asset.__class__.type_
        key = asset.key

        self._data[type_][key] = asset
        logger.info(f"{type_} with key '{key}' has been created.")

        return asset

    def get(self, type_, key: str, log: bool = True):
        """Return asset."""
        try:
            return self._data[type_][key]
        except KeyError:
            if log:
                logger.error(f"{type_} with key '{key}' not found.")
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def list(self, type_):
        """"List assets."""
        return list(self._data[type_].values())

    def update(self, asset):
        type_ = asset.__class__.type_
        key = asset.key

        if key not in self._data[type_]:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

        self._data[type_][key] = asset
        return asset
