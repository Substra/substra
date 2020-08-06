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
import pathlib
import tempfile
import typing

from substra.sdk import exceptions, schemas
from substra.sdk.backends.remote import backend
from substra.sdk.backends.local import db, models

_LOCAL_KEY = "local_"


class DataAccess:
    """Data access layer.

    This is an intermediate layer between the backend and the local/remote data access.
    """

    def __init__(self, remote_backend: typing.Optional[backend.Remote]):
        self._db = db.get()
        self._remote = remote_backend
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="/tmp/")

    @property
    def tmp_dir(self):
        return pathlib.Path(self._tmp_dir.name)

    @staticmethod
    def is_local(key: str):
        """Check if the key corresponds to a local
        or remote asset.
        """
        return key.startswith(_LOCAL_KEY)

    @staticmethod
    def get_local_key(key: str):
        """Transform a key into a 'local' key.
        """
        return _LOCAL_KEY + key

    def _get_asset_content_filename(self, type_):
        if type_ in [
            schemas.Type.Algo,
            schemas.Type.AggregateAlgo,
            schemas.Type.CompositeAlgo
        ]:
            asset_name = "algo.tar.gz"
            field_name = "content"

        elif type_ == schemas.Type.Dataset:
            asset_name = "opener.py"
            field_name = "opener"

        elif type_ == schemas.Type.Objective:
            asset_name = "metrics.zip"
            field_name = "metrics"

        else:
            raise ValueError(f"Cannot download this type of asset {type_}")

        return asset_name, field_name

    def _get_response(self, type_, asset):
        return models.SCHEMA_TO_MODEL[type_].from_response(asset)

    def login(self, username, password):
        if self._remote:
            self._remote.login(username, password)

    def add(self, asset, exist_ok: bool = False):
        return self._db.add(asset, exist_ok=exist_ok)

    def remote_download(self, asset_type, url_field_path, key, destination):
        self._remote.download(asset_type, url_field_path, key, destination)

    def get_remote_description(self, asset_type, key):
        return self._remote.describe(asset_type, key)

    def get_with_files(self, type_: schemas.Type, key: str):
        """Get the asset with files on the local disk for execution.
        This does not load the description as it is not required for execution.
        """
        if self.is_local(key):
            return self._db.get(type_, key)
        else:
            asset_name, field_name = self._get_asset_content_filename(type_)
            asset = self._get_response(
                type_,
                self._remote.get(type_, key)
            )
            tmp_directory = self.tmp_dir / key
            asset_path = tmp_directory / asset_name

            if not tmp_directory.exists():
                pathlib.Path.mkdir(tmp_directory)

                self._remote.download(
                    type_,
                    field_name + ".storageAddress",
                    key,
                    asset_path,
                )

            attr = getattr(asset, field_name)
            attr.storage_address = asset_path
            return asset

    def get(self, type_, key: str):
        if self.is_local(key):
            return self._db.get(type_, key)
        elif self._remote:
            return self._get_response(type_, self._remote.get(type_, key))
        else:
            # TODO: better error that says do not have a remote ?
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def list(self, type_):
        """"List assets."""
        local_assets = self._db.list(type_)
        remote_assets = list()
        if self._remote:
            for asset in self._remote.list(type_):
                remote_assets.append(
                    self._get_response(type_, asset)
                )
        return local_assets + remote_assets

    def update(self, asset):
        return self._db.update(asset)
