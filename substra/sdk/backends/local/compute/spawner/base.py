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
