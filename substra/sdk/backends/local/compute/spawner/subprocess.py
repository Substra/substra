import logging
import os
import pathlib
import re
import shutil
import string
import subprocess
import sys
import tempfile
import typing

from substra.sdk.archive import uncompress
from substra.sdk.backends.local.compute.spawner.base import VOLUME_INPUTS
from substra.sdk.backends.local.compute.spawner.base import BaseSpawner
from substra.sdk.backends.local.compute.spawner.base import ExecutionError
from substra.sdk.backends.local.compute.spawner.base import write_command_args_file

logger = logging.getLogger(__name__)

PYTHON_SCRIPT_REGEX = r"(?<=\")([^\"]*\.py)(?=\")"
METHOD_REGEX = r"\"\-\-function-name\"\,\s*\"([^\"]*)\""


def _get_entrypoint_from_dockerfile(tmpdir):
    """
    Extracts the .py script and the function name to execute in
    an ENTRYPOINT line of a Dockerfile, located in tmpdir.
    For instance if the line `ENTRYPOINT ["python3", "function.py", "--function-name", "train"]` is in the Dockerfile,
     `function.py`, `train` is extracted.
    """
    valid_example = (
        """The entry point should be specified as follow: """
        """``ENTRYPOINT ["<executor>", "<function_file.py>", "--function-name", "<method name>"]"""
    )
    with open(tmpdir / "Dockerfile") as f:
        for line in f:
            if "ENTRYPOINT" not in line:
                continue

            script_name = re.findall(PYTHON_SCRIPT_REGEX, line)
            if len(script_name) != 1:
                raise ExecutionError("Couldn't extract script from ENTRYPOINT line in Dockerfile", valid_example)

            function_name = re.findall(METHOD_REGEX, line)
            if len(function_name) != 1:
                raise ExecutionError("Couldn't extract method name from ENTRYPOINT line in Dockerfile", valid_example)

            return script_name[0], function_name[0]

    raise ExecutionError("Couldn't get entrypoint in Dockerfile", valid_example)


def _get_command_args(
    function_name: str, args_template: typing.List[string.Template], local_volumes: typing.Dict[str, str]
) -> typing.List[str]:
    args = ["--function-name", str(function_name)]
    args += [tpl.substitute(**local_volumes) for tpl in args_template]
    return args


def _symlink_data_samples(data_sample_paths: typing.Dict[str, pathlib.Path], dest_dir: str):
    """Create a symbolic link to "move" the data samples
    to the data directory.

    Args:
        data_sample_paths (typing.Dict[str, pathlib.Path]): Paths to the samples
        dest_dir (str): Temp data directory
    """
    # Check if there are already data samples in the dest dir (testtasks are executed in 2 parts)
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
        command_args_tpl: typing.List[string.Template],
        data_sample_paths: typing.Optional[typing.Dict[str, pathlib.Path]],
        local_volumes,
        envs,
    ):
        """Spawn a python process (blocking)."""
        with tempfile.TemporaryDirectory(dir=self._local_worker_dir) as function_dir:
            with tempfile.TemporaryDirectory(dir=function_dir) as args_dir:
                function_dir = pathlib.Path(function_dir)
                args_dir = pathlib.Path(args_dir)
                uncompress(archive_path, function_dir)
                script_name, function_name = _get_entrypoint_from_dockerfile(function_dir)

                args_file = args_dir / "arguments.txt"

                py_command = [sys.executable, str(function_dir / script_name), f"@{args_file}"]
                py_command_args = _get_command_args(function_name, command_args_tpl, local_volumes)
                write_command_args_file(args_file, py_command_args)

                if data_sample_paths is not None and len(data_sample_paths) > 0:
                    _symlink_data_samples(data_sample_paths, local_volumes[VOLUME_INPUTS])

                # Catching error and raising to be ISO to the docker local backend
                # Don't capture the output to be able to use pdb
                try:
                    subprocess.run(py_command, capture_output=False, check=True, cwd=function_dir, env=envs)
                except subprocess.CalledProcessError as e:
                    raise ExecutionError(e)
