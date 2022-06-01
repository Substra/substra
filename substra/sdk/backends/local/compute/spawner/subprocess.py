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
import os
import pathlib
import re
import shlex
import shutil
import string
import subprocess
import sys
import tempfile
import typing

from substra.sdk.archive import uncompress
from substra.sdk.backends.local.compute.spawner.base import BaseSpawner
from substra.sdk.backends.local.compute.spawner.base import ExecutionError

logger = logging.getLogger(__name__)

# Find a name between quotes ending by '.py'
PYTHON_SCRIPT_NAME = r"(?<=\")([^\"]*\.py)(?=\")"


def _get_script_name_from_dockerfile(tmpdir):
    """
    Extracts the .py script in an ENTRYPOINT line of a Dockerfile, located in tmpdir.
    For instance if the line `ENTRYPOINT ["python3", "algo.py"]` is in the Dockerfile,
     `algo.py` is extracted.
    """
    with open(tmpdir / "Dockerfile") as f:
        for line in f:
            if "ENTRYPOINT" not in line:
                continue

            script_name = re.findall(PYTHON_SCRIPT_NAME, line)
            if not script_name:
                raise ExecutionError(f"Couldn't get Python script in Dockerfile's entrypoint : {line}")

            return script_name[0]

    raise ExecutionError("Couldn't get entrypoint in Dockerfile")


def _get_py_command(script_name, tmpdir, command_template, local_volumes):
    """
    Substitute the local_volumes in the command_template and split it to have the
    py_command

    Args:
        script_name (str): the name of the script
        tmpdir (pathlib.Path): the tmpdir in which the subprocess mode is running
        command_template (string.Template): template containing all arguments for the subprocess
        local_volumes (dict[str, str]): paths to substitute in command_template

    Returns:
        py_command (list[str]): the list with all commands for the subprocess
    """
    # modify local_volumes not to split paths with spaces
    local_volumes = {k: str(v).replace(" ", r"\\\\") for k, v in local_volumes.items()}
    # replace volumes variables by local volumes
    command = command_template.substitute(**local_volumes)
    # split command to run into subprocess
    command_args = shlex.split(command)
    # replace paths with spaces that were modified
    # Not using regex as shlex replaced '\' with '\\' automatically. Hence '\\\\' which was represented as '\\' is now
    # '\\\\'
    command_args = [command_arg.replace("\\\\", " ") for command_arg in command_args]
    # put current python interpreter and script to launch before script command
    py_command = [sys.executable, str(tmpdir / script_name)]
    py_command.extend(command_args)

    return py_command


def _symlink_data_samples(data_sample_paths: typing.Dict[str, pathlib.Path], dest_dir: str):
    """Create a symbolic link to "move" the data samples
    to the data directory.

    Args:
        data_sample_paths (typing.Dict[str, pathlib.Path]): Paths to the samples
        dest_dir (str): Temp data directory
    """
    # Check if there are already data samples in the dest dir (testtuples are executed in 2 parts)
    sample_key = next(iter(data_sample_paths))
    if (pathlib.Path(dest_dir) / sample_key).exists():
        return
    # copy the whole tree but using hard link to be fast and not use too much place
    for sample_key, sample_path in data_sample_paths.items():
        dest_path = pathlib.Path(dest_dir) / sample_key
        shutil.copytree(sample_path, dest_path, copy_function=os.symlink)


class Subprocess(BaseSpawner):
    """Wrapper to execute a command in a python process."""

    def __init__(self, local_worker_dir: pathlib.Path):
        super().__init__(local_worker_dir=local_worker_dir)

    def spawn(
        self,
        name,
        archive_path,
        command_template: string.Template,
        data_sample_paths: typing.Optional[typing.Dict[str, pathlib.Path]],
        local_volumes,
        envs,
    ):
        """Spawn a python process (blocking)."""
        with tempfile.TemporaryDirectory(dir=self._local_worker_dir) as tmpdir:
            tmpdir = pathlib.Path(tmpdir)
            uncompress(archive_path, tmpdir)
            # TODO: use new generated venv from dockerfile (pip install substratools,...)
            script_name = _get_script_name_from_dockerfile(tmpdir)
            # get py_command for subprocess
            py_command = _get_py_command(script_name, tmpdir, command_template, local_volumes)

            if data_sample_paths is not None:
                assert "_VOLUME_INPUT_DATASAMPLES" in local_volumes, (
                    "if there are data samples" + "then there must be a Docker volume"
                )
                _symlink_data_samples(data_sample_paths, local_volumes["_VOLUME_INPUT_DATASAMPLES"])

            # Catching error and raising to be ISO to the docker local backend
            # Don't capture the output to be able to use pdb
            try:
                subprocess.run(py_command, capture_output=False, check=True, cwd=tmpdir, env=envs)
            except subprocess.CalledProcessError as e:
                raise ExecutionError(e)
