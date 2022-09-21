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
from substra.sdk.backends.local.compute.spawner.base import BaseSpawner
from substra.sdk.backends.local.compute.spawner.base import ExecutionError

logger = logging.getLogger(__name__)

PYTHON_SCRIPT_REGEX = r"(?<=\")([^\"]*\.py)(?=\")"
METHOD_REGEX = r"\"\-\-method-name\"\,\s*\"([^\"]*)\""


def _get_entrypoint_from_dockerfile(tmpdir):
    """
    Extracts the .py script and the function name to execute in
    an ENTRYPOINT line of a Dockerfile, located in tmpdir.
    For instance if the line `ENTRYPOINT ["python3", "algo.py", "--method-name", "train"]` is in the Dockerfile,
     `algo.py`, `train` is extracted.
    """
    valid_example = (
        """The entry point should be specified as follow: """
        """``ENTRYPOINT ["<executor>", "<algo_file.py>", "--method-name", "<method name>"]"""
    )
    with open(tmpdir / "Dockerfile") as f:
        for line in f:
            if "ENTRYPOINT" not in line:
                continue

            script_name = re.findall(PYTHON_SCRIPT_REGEX, line)
            if len(script_name) != 1:
                raise ExecutionError("Couldn't extract script from ENTRYPOINT line in Dockerfile", valid_example)

            method_name = re.findall(METHOD_REGEX, line)
            if len(method_name) != 1:
                raise ExecutionError("Couldn't extract method name from ENTRYPOINT line in Dockerfile", valid_example)

            return script_name[0], method_name[0]

    raise ExecutionError("Couldn't get entrypoint in Dockerfile", valid_example)


def _get_command_args(
    method_name: str, command_template: typing.List[string.Template], local_volumes: typing.Dict[str, str]
) -> typing.List[str]:
    command_args = ["--method-name", str(method_name)]
    command_args += [tpl.substitute(**local_volumes) for tpl in command_template]
    return command_args


def _write_args_file(args_file: pathlib.Path, command_args: typing.List[str]) -> None:
    with open(args_file, "w") as f:
        for item in command_args:
            # one line per argument, see https://docs.python.org/3/library/argparse.html#fromfile-prefix-chars
            f.write(item + "\n")


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
            args_file = tmpdir / "arguments.txt"
            uncompress(archive_path, tmpdir)
            script_name, method_name = _get_entrypoint_from_dockerfile(tmpdir)

            # For the @arguments.txt syntax, see https://docs.python.org/3/library/argparse.html#fromfile-prefix-chars
            py_command = [sys.executable, str(tmpdir / script_name), f"@{args_file}"]
            py_command_args = _get_command_args(method_name, command_template, local_volumes)
            _write_args_file(args_file, py_command_args)

            if data_sample_paths is not None and len(data_sample_paths) > 0:
                _symlink_data_samples(data_sample_paths, local_volumes["_VOLUME_INPUTS"])

            # Catching error and raising to be ISO to the docker local backend
            # Don't capture the output to be able to use pdb
            try:
                subprocess.run(py_command, capture_output=False, check=True, cwd=tmpdir, env=envs)
            except subprocess.CalledProcessError as e:

                raise ExecutionError(e)
