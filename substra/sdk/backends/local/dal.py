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
import logging
import pathlib
import shutil
import tempfile
import typing

from substra.sdk import exceptions, schemas
from substra.sdk.backends.remote import backend
from substra.sdk.backends.local import db

_LOCAL_KEY = "local_"
logger = logging.getLogger(__name__)


class DataAccess:
    """Data access layer.

    This is an intermediate layer between the backend and the local/remote data access.
    """

    def __init__(self, remote_backend: typing.Optional[backend.Remote]):
        self._db = db.InMemoryDb()
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

    def login(self, username, password):
        if self._remote:
            self._remote.login(username, password)

    def add(self, asset):
        return self._db.add(asset)

    def remote_download(self, asset_type, url_field_path, key, destination):
        self._remote.download(asset_type, url_field_path, key, destination)

    def remote_download_model(self, key, destination_file):
        self._remote.download_model(key, destination_file)

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
            asset = self._remote.get(type_, key)
            tmp_directory = self.tmp_dir / key
            asset_path = tmp_directory / asset_name

            if not tmp_directory.exists():
                pathlib.Path.mkdir(tmp_directory)

                self._remote.download(
                    type_,
                    field_name + ".storage_address",
                    key,
                    asset_path,
                )

            attr = getattr(asset, field_name)
            attr.storage_address = asset_path
            return asset

    def get(self, type_, key: str, log: bool = True):
        if self.is_local(key):
            if type_ == schemas.Type.Model:
                return self._get_local_model(key)
            else:
                return self._db.get(type_, key, log)
        elif self._remote:
            return self._remote.get(type_, key)
        else:
            # TODO: better error that says do not have a remote ?
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def list(self, type_, filters):
        """"List assets."""
        local_assets = self._db.list(type_)
        remote_assets = list()
        if self._remote:
            try:
                remote_assets = self._remote.list(type_, filters)
            except Exception as e:
                logger.info(
                    f"Could not list assets from the remote platform:\n{e}. \
                    \nIf you are not logged to a remote platform, ignore this message."
                )
        return local_assets + remote_assets

    def save_file(self,
                  file_path: typing.Union[str, pathlib.Path],
                  key: str):
        """Copy file or directory into the local temp dir to mimick
        the remote backend that saves the files given by the user.
        """
        tmp_directory = self.tmp_dir / key
        tmp_file = tmp_directory / pathlib.Path(file_path).name

        if not tmp_directory.exists():
            pathlib.Path.mkdir(tmp_directory)

        if tmp_file.exists():
            raise exceptions.AlreadyExists(
                f"File {tmp_file.name} already exists for asset {key}",
                409
            )
        elif pathlib.Path(file_path).is_file():
            shutil.copyfile(
                file_path,
                tmp_file
            )
        elif pathlib.Path(file_path).is_dir():
            shutil.copytree(
                file_path,
                tmp_file
            )
        else:
            raise exceptions.InvalidRequest(
                f"Could not copy {file_path}",
                400
            )
        return tmp_file

    def update(self, asset):
        return self._db.update(asset)

    def _get_local_model(self, key):

        for t in self.list(schemas.Type.Traintuple, filters=None):
            if t.out_model and t.out_model.key == key:
                return t.out_model

        for t in self.list(schemas.Type.CompositeTraintuple, filters=None):
            if t.out_head_model.out_model and t.out_head_model.out_model.key == key:
                return t.out_head_model.out_model
            if t.out_trunk_model.out_model and t.out_trunk_model.out_model.key == key:
                return t.out_trunk_model.out_model

        for t in self.list(schemas.Type.Aggregatetuple, filters=None):
            if t.out_model and t.out_model.key == key:
                return t.out_model

        raise exceptions.NotFound(f"Wrong pk {key}", 404)
