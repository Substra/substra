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
import string
import tempfile
import docker
from substra.sdk.backends.local.compute.spawner.base import BaseSpawner, ExecutionError
from substra.sdk.archive import uncompress

logger = logging.getLogger(__name__)

_DOCKER_CONTAINER_MODEL_PATH = "/sandbox/model"

DOCKER_VOLUMES = {
    "_VOLUME_INPUT_DATASAMPLES": {"bind": "/sandbox/data", "mode": "ro"},
    "_VOLUME_MODELS_RO": {"bind": _DOCKER_CONTAINER_MODEL_PATH, "mode": "ro"},
    "_VOLUME_MODELS_RW": {"bind": _DOCKER_CONTAINER_MODEL_PATH, "mode": "rw"},
    "_VOLUME_OPENER": {"bind": "/sandbox/opener/__init__.py", "mode": "ro"},
    "_VOLUME_OUTPUT_PRED": {"bind": "/sandbox/pred", "mode": "rw"},
    "_VOLUME_LOCAL": {"bind": "/sandbox/local", "mode": "rw"},
    "_VOLUME_CHAINKEYS": {"bind": "/sandbox/chainkeys", "mode": "rw"},
    "_VOLUME_INPUT_MODELS_RO": {"bind": "/sandbox/input_models", "mode": "ro"},
    "_VOLUME_OUTPUT_MODELS_RW": {"bind": "/sandbox/output_models", "mode": "rw"},
}


class Docker(BaseSpawner):
    """Wrapper around docker daemon to execute a command in a container."""

    def __init__(self, local_worker_dir: pathlib.Path):
        try:
            self._docker = docker.from_env()
        except docker.errors.DockerException as e:
            raise ConnectionError(
                "Couldn't get the Docker client from environment variables. "
                "Is your Docker server running ?\n"
                "Docker error : {0}".format(e)
            )
        super().__init__(local_worker_dir=local_worker_dir)

    def spawn(
        self,
        name,
        archive_path,
        command_template: string.Template,
        local_volumes=None,
        envs=None,
    ):
        """Spawn a docker container (blocking)."""
        with tempfile.TemporaryDirectory(dir=self._local_worker_dir) as tmpdir:
            uncompress(archive_path, tmpdir)
            try:
                self._docker.images.build(path=tmpdir, tag=name, rm=True)
            except docker.errors.BuildError as exc:
                for line in exc.build_log:
                    if 'stream' in line:
                        logger.error(line['stream'].strip())
                raise

        # format the command to replace each occurrence of a DOCKER_VOLUMES's key
        # by its "bind" value
        volumes_format = {
            volume_name: volume_path["bind"]
            for volume_name, volume_path in DOCKER_VOLUMES.items()
        }
        command = command_template.substitute(**volumes_format)

        # create the volumes dict for docker by binding the local_volumes and the DOCKER_VOLUME
        volumes_docker = {
            volume_path: DOCKER_VOLUMES[volume_name]
            for volume_name, volume_path in local_volumes.items()
        }

        container = self._docker.containers.run(
            name,
            command=command,
            volumes=volumes_docker or {},
            environment=envs,
            remove=False,
            detach=True,
            tty=True,
            stdin_open=True,
            shm_size='8G',
        )

        execution_logs = []
        for line in container.logs(stream=True, stdout=True, stderr=True):
            execution_logs.append(line.decode('utf-8'))

        r = container.wait()
        execution_logs = ''.join(execution_logs)
        exit_code = r['StatusCode']
        if exit_code != 0:
            logger.error(f"\n\nExecution logs: {execution_logs}")
            raise ExecutionError(f"Container '{name}' exited with status code '{exit_code}'")

        container.remove()
        return execution_logs
