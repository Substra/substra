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
import os
import tarfile
import tempfile
import zipfile

import docker

from substra.sdk import exceptions

_DOCKER = docker.from_env()
_USER = os.getuid()


def _untar(archive, to_):
    with tarfile.open(archive) as tf:
        tf.extractall(to_)


def _unzip(archive, to_):
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(to_)


def _uncompress(archive, to_):
    """Uncompress tar or zip archive to destination."""
    if archive.endswith('.zip'):
        handler = _unzip
    elif archive.endswith('.tgz') or archive.endswith('.tar.gz'):
        handler = _untar
    else:
        raise exceptions.InvalidRequest(f"Cannot uncompres '{archive}'", 400)

    handler(archive, to_)


class ExecutionError(Exception):
    pass


class DockerSpawner:
    """Wrapper around docker daemon to execute a command in a container."""

    def spawn(self, name, archive_path, command, volumes=None, envs=None):
        """Spawn a docker container (blocking)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _uncompress(archive_path, tmpdir)
            _DOCKER.images.build(path=tmpdir, tag=name, rm=True)

        container = _DOCKER.containers.run(
            name,
            command=command,
            volumes=volumes or {},
            environment=envs,
            remove=False,
            user=_USER,
            userns_mode="host",
            detach=True,
            tty=True,
            stdin_open=True,
        )

        execution_logs = []
        for line in container.logs(stream=True, stdout=True, stderr=True):
            execution_logs.append(line.decode('utf-8'))

        r = container.wait()
        execution_logs = ''.join(execution_logs)
        exit_code = r['StatusCode']
        if exit_code != 0:
            print(f"\n\nExecution logs: {execution_logs}")
            raise ExecutionError(f"Container '{name}' exited with status code '{exit_code}'")

        container.remove()
        return execution_logs


def get():
    return DockerSpawner()
