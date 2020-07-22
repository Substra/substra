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

    def _get_response(self, type_, asset):
        return models.SCHEMA_TO_MODEL[type_].from_response(asset)

    def login(self, username, password):
        if self._remote:
            self._remote.login(username, password)

    def add(self, asset, exist_ok: bool = False):
        return self._db.add(asset, exist_ok=exist_ok)

    def download_dataset(self, key: str):
        if key.startswith('local_'):
            return self._db.get(schemas.Type.Dataset, key)
        elif self._remote:
            dataset = self._get_response(
                schemas.Type.Dataset,
                self._remote.get(schemas.Type.Dataset, key)
            )

            tmp_directory = self.tmp_dir / key
            dataset_description_path = tmp_directory / "dataset_description.md"

            if not tmp_directory.exists():
                pathlib.Path.mkdir(tmp_directory)
                self._remote.download(
                    schemas.Type.Dataset,
                    'opener.storageAddress',
                    key,
                    tmp_directory / 'opener.py',
                )

                dataset_description = self._remote.describe(schemas.Type.Dataset, key=key)
                with dataset_description_path.open("w", encoding='utf-8') as f:
                    f.write(dataset_description)

            dataset.description.storage_address = dataset_description_path
            dataset.opener.storage_address = tmp_directory / "opener.py"

            return dataset
        else:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def download_algo(self, key: str):
        if key.startswith('local_'):
            return self._db.get(schemas.Type.Algo, key)
        elif self._remote:
            algo = self._get_response(
                schemas.Type.Algo,
                self._remote.get(schemas.Type.Algo, key)
            )
            tmp_directory = self.tmp_dir / key
            algo_path = tmp_directory / 'algo.tar.gz'
            algo_description_path = tmp_directory / "algo_description.md"
            if not tmp_directory.exists():
                pathlib.Path.mkdir(tmp_directory)
                self._remote.download(
                    schemas.Type.Algo,
                    'content.storageAddress',
                    key,
                    algo_path
                )
                algo_description = self._remote.describe(schemas.Type.Algo, key)
                with algo_description_path.open("w", encoding='utf-8') as f:
                    f.write(algo_description)
            algo.file = algo_path
            algo.description.storage_address = algo_description_path
            return algo
        else:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def download_objective(self, key: str):
        if key.startswith('local_'):
            return self._db.get(schemas.Type.Objective, key)
        elif self._remote:
            objective = self._get_response(
                schemas.Type.Objective,
                self._remote.get(schemas.Type.Objective, key)
            )
            tmp_directory = self.tmp_dir / key
            metrics_path = tmp_directory / 'metrics.zip'
            description_path = tmp_directory / "description.md"
            if not tmp_directory.exists():
                pathlib.Path.mkdir(tmp_directory)
                self._remote.download(
                    schemas.Type.Objective,
                    'metrics.storageAddress',
                    key,
                    metrics_path
                )
                description = self._remote.describe(schemas.Type.Objective, key)
                with description_path.open("w", encoding='utf-8') as f:
                    f.write(description)
            objective.metrics.storage_address = metrics_path
            objective.description.storage_address = description_path
            return objective
        else:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def get(self, type_, key: str):
        # Test on whether the key starts with local_
        if key.startswith('local_'):
            return self._db.get(type_, key)
        elif self._remote:
            return self._get_response(type_, self._remote.get(type_, key))
        else:
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