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
import re
import string
import subprocess
import sys
import tempfile

from substra.sdk.backends.local.compute.spawner.base import ExecutionError, BaseSpawner
from substra.sdk.archive import uncompress

logger = logging.getLogger(__name__)

# Find a name between quotes ending by '.py'
PYTHON_SCRIPT_NAME = r'(?<=\")([^\"]*\.py)(?=\")'


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
                raise ExecutionError(
                    f"Couldn't get Python script in Dockerfile's entrypoint : {line}"
                )

            return script_name[0]

    raise ExecutionError("Couldn't get entrypoint in Dockerfile")


def _get_py_command(script_name, tmpdir, command_template, local_volumes):
    """
    Substitute the local_volumes in the command_template ans split it to have the
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
    local_volumes = {k: str(v).replace(" ", "\\\\") for k, v in local_volumes.items()}
    # replace volumes variables by local volumes
    command = command_template.substitute(**local_volumes)
    # split command to run into subprocess
    command_args = command.split()
    # replace paths with spaces that were modified
    command_args = [command_arg.replace("\\\\", " ") for command_arg in command_args]
    # put current python interpreter and script to launch before script command
    py_command = [sys.executable, str(tmpdir / script_name)]
    py_command.extend(command_args)

    return py_command


class Subprocess(BaseSpawner):
    """Wrapper to execute a command in a python process."""

    def __init__(self, local_worker_dir: pathlib.Path):
        super().__init__(local_worker_dir=local_worker_dir)

    def spawn(
        self,
        name,
        archive_path,
        command_template: string.Template,
        local_volumes=None,
        envs=None,
    ):
        """Spawn a python process (blocking)."""
        with tempfile.TemporaryDirectory(dir=self._local_worker_dir) as tmpdir:
            tmpdir = pathlib.Path(tmpdir)
            uncompress(archive_path, tmpdir)
            # TODO: use new generated venv from dockerfile (pip install substratools,...)
            script_name = _get_script_name_from_dockerfile(tmpdir)
            # get py_command for subprocess
            py_command = _get_py_command(script_name, tmpdir, command_template, local_volumes)
            # run subprocess
            try:
                process = subprocess.run(py_command,
                                         capture_output=True,
                                         check=True,
                                         cwd=tmpdir,
                                         env=envs)
            except subprocess.CalledProcessError as exc:
                logger.error(exc)
                logger.error(exc.stderr.decode('UTF-8'))
                logger.error(exc.stdout.decode('UTF-8'))
                raise ExecutionError(
                    f"Subprocess '{name}' exited with status code '{exc.returncode}'"
                )

        execution_logs = str(process)
        execution_logs += str(process.stderr.decode('UTF-8'))
        execution_logs += str(process.stdout.decode('UTF-8'))

        return execution_logs
