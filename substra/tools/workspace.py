import abc
import os


def makedir_safe(path):
    """Create dir (no failure)."""
    try:
        os.makedirs(path)
    except (FileExistsError, PermissionError):
        pass


DEFAULT_INPUT_DATA_FOLDER_PATH = "data/"
DEFAULT_INPUT_PREDICTIONS_PATH = "pred/pred"
DEFAULT_OUTPUT_PERF_PATH = "pred/perf.json"
DEFAULT_LOG_PATH = "model/log_model.log"
DEFAULT_CHAINKEYS_PATH = "chainkeys/"


class Workspace(abc.ABC):
    """Filesystem workspace for task execution."""

    def __init__(self, dirpath=None):
        self._workdir = dirpath if dirpath else os.getcwd()

    def _get_default_path(self, path):
        return os.path.join(self._workdir, path)

    def _get_default_subpaths(self, path):
        rootpath = os.path.join(self._workdir, path)
        if os.path.isdir(rootpath):
            return [
                os.path.join(rootpath, subfolder)
                for subfolder in os.listdir(rootpath)
                if os.path.isdir(os.path.join(rootpath, subfolder))
            ]
        return []


class OpenerWorkspace(Workspace):
    """Filesystem workspace required by the opener."""

    def __init__(
        self,
        dirpath=None,
        input_data_folder_paths=None,
    ):
        super().__init__(dirpath=dirpath)

        assert input_data_folder_paths is None or isinstance(input_data_folder_paths, list)

        self.input_data_folder_paths = input_data_folder_paths or self._get_default_subpaths(
            DEFAULT_INPUT_DATA_FOLDER_PATH
        )


class FunctionWorkspace(Workspace):
    """Filesystem workspace for user defined function execution."""

    def __init__(
        self,
        dirpath=None,
        log_path=None,
        chainkeys_path=None,
        inputs=None,
        outputs=None,
    ):

        super().__init__(dirpath=dirpath)

        self.input_data_folder_paths = (
            self._get_default_subpaths(DEFAULT_INPUT_DATA_FOLDER_PATH)
            if inputs is None
            else inputs.input_data_folder_paths
        )

        self.log_path = log_path or self._get_default_path(DEFAULT_LOG_PATH)
        self.chainkeys_path = chainkeys_path or self._get_default_path(DEFAULT_CHAINKEYS_PATH)

        self.opener_path = inputs.opener_path if inputs else None

        self.task_inputs = inputs.formatted_dynamic_resources if inputs else {}
        self.task_outputs = outputs.formatted_dynamic_resources if outputs else {}

        dirs = [
            self.chainkeys_path,
        ]
        paths = [
            self.log_path,
        ]

        dirs.extend([os.path.dirname(p) for p in paths])
        for d in dirs:
            if d:
                makedir_safe(d)
