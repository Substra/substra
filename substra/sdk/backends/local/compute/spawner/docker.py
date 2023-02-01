import logging
import pathlib
import shutil
import string
import tempfile
import typing

import docker

from substra.sdk.archive import uncompress
from substra.sdk.backends.local.compute.spawner.base import VOLUME_CLI_ARGS
from substra.sdk.backends.local.compute.spawner.base import VOLUME_INPUTS
from substra.sdk.backends.local.compute.spawner.base import VOLUME_OUTPUTS
from substra.sdk.backends.local.compute.spawner.base import BaseSpawner
from substra.sdk.backends.local.compute.spawner.base import BuildError
from substra.sdk.backends.local.compute.spawner.base import ExecutionError
from substra.sdk.backends.local.compute.spawner.base import write_command_args_file

logger = logging.getLogger(__name__)

ROOT_DIR = "/substra_internal"
DOCKER_VOLUMES = {
    VOLUME_INPUTS: {"bind": f"{ROOT_DIR}/inputs", "mode": "ro"},
    VOLUME_OUTPUTS: {"bind": f"{ROOT_DIR}/outputs", "mode": "rw"},
    VOLUME_CLI_ARGS: {"bind": f"{ROOT_DIR}/cli-args", "mode": "rw"},
}


def _copy_data_samples(data_sample_paths: typing.Dict[str, pathlib.Path], dest_dir: str):
    """Move the data samples to the data directory.

    We copy the data samples even though it is slow because:

    - symbolic links do not work with Docker container volumes
    - hard links cannot be created across partitions
    - mounting each data sample as its own volume causes permission errors

    Args:
        data_sample_paths (typing.Dict[str, pathlib.Path]): Paths to the samples
        dest_dir (str): Temp data directory
    """
    # Check if there are already data samples in the dest dir (testtasks are executed in 2 parts)
    sample_key = next(iter(data_sample_paths))
    if (pathlib.Path(dest_dir) / sample_key).exists():
        return
    # copy the whole tree
    for sample_key, sample_path in data_sample_paths.items():
        dest_path = pathlib.Path(dest_dir) / sample_key
        shutil.copytree(sample_path, dest_path)


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

    def _build_docker_image(self, name: str, archive_path: pathlib.Path):
        """Spawn a docker container (blocking)."""
        with tempfile.TemporaryDirectory(dir=self._local_worker_dir) as tmpdir:
            image_exists = False
            try:
                self._docker.images.get(name=name)
                image_exists = True
            except docker.errors.ImageNotFound:
                pass

            if not image_exists:
                try:
                    logger.debug("Did not find the Docker image %s - building it", name)
                    uncompress(archive_path, tmpdir)
                    self._docker.images.build(path=tmpdir, tag=name, rm=True)
                except docker.errors.BuildError as exc:
                    log = ""
                    for line in exc.build_log:
                        if "stream" in line:
                            log += line["stream"].strip()
                    logger.error(log)
                    raise BuildError(log)

    def spawn(
        self,
        name: str,
        archive_path: pathlib.Path,
        command_args_tpl: typing.List[string.Template],
        data_sample_paths: typing.Optional[typing.Dict[str, pathlib.Path]],
        local_volumes: typing.Optional[dict],
        envs: typing.Optional[typing.List[str]],
    ):
        """Build the docker image, copy the data samples then spawn a Docker container
        and execute the task.
        """
        self._build_docker_image(name=name, archive_path=archive_path)

        # format the command to replace each occurrence of a DOCKER_VOLUMES's key
        # by its "bind" value
        volumes_format = {volume_name: volume_path["bind"] for volume_name, volume_path in DOCKER_VOLUMES.items()}
        command_args = [tpl.substitute(**volumes_format) for tpl in command_args_tpl]

        if data_sample_paths is not None and len(data_sample_paths) > 0:
            _copy_data_samples(data_sample_paths, local_volumes[VOLUME_INPUTS])

        args_filename = "arguments.txt"
        args_path_local = pathlib.Path(local_volumes[VOLUME_CLI_ARGS]) / args_filename
        # Pathlib is incompatible here for Windows, as it would create a "WindowsPath"
        args_path_docker = DOCKER_VOLUMES[VOLUME_CLI_ARGS]["bind"] + "/" + args_filename
        write_command_args_file(args_path_local, command_args)

        # create the volumes dict for docker by binding the local_volumes and the DOCKER_VOLUME
        volumes_docker = {
            volume_path: DOCKER_VOLUMES[volume_name] for volume_name, volume_path in local_volumes.items()
        }

        container = self._docker.containers.run(
            name,
            command=f"@{args_path_docker}",
            volumes=volumes_docker or {},
            environment=envs,
            remove=False,
            detach=True,
            tty=True,
            stdin_open=True,
            shm_size="8G",
        )

        execution_logs = []
        for line in container.logs(stream=True, stdout=True, stderr=True):
            execution_logs.append(line.decode("utf-8"))

        r = container.wait()
        execution_logs_str = "".join(execution_logs)
        exit_code = r["StatusCode"]
        if exit_code != 0:
            logger.error("\n\nExecution logs: %s", execution_logs_str)
            raise ExecutionError(f"Container '{name}' exited with status code '{exit_code}'")

        container.remove()
