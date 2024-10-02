import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from substratools.task_resources import TaskResources
from substratools.utils import import_module
from substratools.workspace import FunctionWorkspace
from tests.utils import OutputIdentifiers


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-workspace"
    d.mkdir()
    return d


@pytest.fixture(autouse=True)
def patch_cwd(monkeypatch, workdir):
    # this is needed to ensure the workspace is located in a tmpdir
    def getcwd():
        return str(workdir)

    monkeypatch.setattr(os, "getcwd", getcwd)


@pytest.fixture()
def valid_opener_code():
    return """
import json
from substratools import Opener

class FakeOpener(Opener):
    def get_data(self, folder):
        return 'X', list(range(0, 3))

    def fake_data(self, n_samples):
        return ['Xfake'] * n_samples, [0] * n_samples
"""


@pytest.fixture()
def valid_opener(valid_opener_code):
    import_module("opener", valid_opener_code)
    yield
    del sys.modules["opener"]


@pytest.fixture()
def valid_opener_script(workdir, valid_opener_code):
    opener_path = workdir / "my_opener.py"
    opener_path.write_text(valid_opener_code)

    return str(opener_path)


@pytest.fixture(autouse=True)
def output_model_path(workdir: Path) -> str:
    path = workdir / str(uuid4())
    yield path
    if path.exists():
        os.remove(path)


@pytest.fixture(autouse=True)
def output_model_path_2(workdir: Path) -> str:
    path = workdir / str(uuid4())
    yield path
    if path.exists():
        os.remove(path)


@pytest.fixture()
def valid_function_workspace(output_model_path: str) -> FunctionWorkspace:
    workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.shared, "value": str(output_model_path), "multiple": False}])
    )

    workspace = FunctionWorkspace(outputs=workspace_outputs)

    return workspace
