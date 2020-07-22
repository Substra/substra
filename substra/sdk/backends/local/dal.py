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
import re
import typing

from substra.sdk import exceptions
from substra.sdk.backends.remote import backend
from substra.sdk.backends.local import db, models


class DataAccess:
    """Data access layer.

    This is an intermediate layer between the backend and the local/remote data access.
    """

    def __init__(self, remote_backend: typing.Optional[backend.Remote]):
        self._db = db.get()
        self._remote = remote_backend

    def login(self, username, password):
        if self._remote:
            self._remote.login(username, password)

    def add(self, asset, exist_ok: bool = False):
        return self._db.add(asset, exist_ok=exist_ok)

    def get(self, type_, key: str):
        # Test on whether the key starts with local_
        if key.startswith('local_'):
            return self._db.get(type_, key)
        elif self._remote:
            return models.SCHEMA_TO_MODEL[type_].from_response(
                self._remote.get(type_, key)
            )
        else:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def list(self, type_):
        """"List assets."""
        local_assets = self._db.list(type_)
        remote_assets = list()
        if self._remote:
            for asset in self._remote.list(type_):
                remote_assets.append(
                    models.SCHEMA_TO_MODEL[type_].from_response(asset)
                )
        return local_assets + remote_assets

    def update(self, asset):
        return self._db.update(asset)
