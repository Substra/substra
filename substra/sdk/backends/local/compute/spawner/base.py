import abc
import pathlib
import string
import typing

VOLUME_CLI_ARGS = "_VOLUME_CLI_ARGS"
VOLUME_INPUTS = "_VOLUME_INPUTS"
VOLUME_OUTPUTS = "_VOLUME_OUTPUTS"


class BuildError(Exception):
    """An error occurred during the build of the function"""

    pass


class ExecutionError(Exception):
    """An error occurred during the execution of the compute task"""

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
        command_args_tpl: typing.List[string.Template],
        data_sample_paths: typing.Optional[typing.Dict[str, pathlib.Path]],
        local_volumes,
        envs,
    ):
        """Execute archive in a contained environment."""
        raise NotImplementedError


def write_command_args_file(args_file: pathlib.Path, command_args: typing.List[str]) -> None:
    """Write the substra-tools command line arguments to a file.

    The format uses one line per argument. See
    https://docs.python.org/3/library/argparse.html#fromfile-prefix-chars
    """
    with open(args_file, "w") as f:
        for item in command_args:
            f.write(item + "\n")
