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
from substra.sdk.backends.local import models

logger = logging.getLogger(__name__)


class InMemoryDb:
    """In memory data db."""

    def __init__(self):
        # assets stored per type and per key
        self._data = collections.defaultdict(dict)

    def add(self, asset, exist_ok: bool = False):
        """Add an asset."""
        type_ = asset.__class__.type_
        if type_ == models.ComputePlan.type_:
            key = asset.compute_plan_id
        else:
            key = asset.key

        if key in self._data[type_]:
            if not exist_ok:
                raise exceptions.AlreadyExists(key, 409)
            # it already exists, fetch the existing one
            asset = self._data[type_][key]
            logger.info(f"{type_} with key '{key}' has not been created: already exists.")

        else:
            self._data[type_][key] = asset
            logger.info(f"{type_} with key '{key}' has been created.")
        return asset

    def get(self, type_, key: str):
        """Return asset."""
        try:
            return self._data[type_][key]
        except KeyError:
            logger.error(f"{type_} with key '{key}' not found.")
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def list(self, type_):
        """"List assets."""
        return self._data[type_].values()

    def update(self, asset):
        type_ = asset.__class__.type_
        if type_ == models.ComputePlan.type_:
            key = asset.compute_plan_id
        else:
            key = asset.key

        if key not in self._data[type_]:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

        self._data[type_][key] = asset
        return asset


_SHARED_DB = None


def reset():
    global _SHARED_DB
    _SHARED_DB = InMemoryDb()
    return _SHARED_DB


def get():
    global _SHARED_DB
    if not _SHARED_DB:
        reset()
    return _SHARED_DB
