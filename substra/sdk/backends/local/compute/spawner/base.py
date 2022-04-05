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
import abc
import pathlib
import string
import typing


class ExecutionError(Exception):
    pass


class BaseSpawner(abc.ABC):
    """Base wrapper to execute a command"""

    def __init__(self, local_worker_dir: pathlib.Path):
        self._local_worker_dir = local_worker_dir

    @abc.abstractmethod
    def spawn(
        self,
        name,
        archive_path,
        command_template: string.Template,
        data_sample_paths: typing.Optional[typing.Dict[str, pathlib.Path]],
        local_volumes,
        envs,
    ):
        """Execute archive in a contained environment."""
        raise NotImplementedError
