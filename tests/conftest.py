import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

import substra
from substra.sdk.schemas import FunctionSpec

from . import data_factory
from .fl_interface import FLFunctionInputs
from .fl_interface import FLFunctionOutputs
from .fl_interface import FunctionCategory
from substra.tools.task_resources import TaskResources
from substra.tools.utils import import_module
from substra.tools.workspace import FunctionWorkspace
from tests.tools.utils import OutputIdentifiers


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )


@pytest.fixture
def client(tmpdir):
    c = substra.Client(url="http://foo.io", backend_type="remote", token="foo")
    return c


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-workspace"
    d.mkdir()
    return d


@pytest.fixture
def dataset_query(tmpdir):
    opener_path = tmpdir / "opener.py"
    opener_path.write_text("raise ValueError()", encoding="utf-8")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    return {
        "name": "dataset_name",
        "data_opener": str(opener_path),
        "description": str(desc_path),
        "permissions": {
            "public": True,
            "authorized_ids": [],
        },
        "logs_permission": {
            "public": True,
            "authorized_ids": [],
        },
    }


@pytest.fixture
def metric_query(tmpdir):
    metrics_path = tmpdir / "metrics.zip"
    metrics_path.write_text("foo archive", encoding="utf-8")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    return {
        "name": "metrics_name",
        "file": str(metrics_path),
        "description": str(desc_path),
        "permissions": {
            "public": True,
            "authorized_ids": [],
        },
    }


@pytest.fixture
def function_query(tmpdir):
    function_file_path = tmpdir / "function.tar.gz"
    function_file_path.write(b"tar gz archive")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    function_category = FunctionCategory.simple

    return FunctionSpec(
        name="function_name",
        inputs=FLFunctionInputs[function_category],
        outputs=FLFunctionOutputs[function_category],
        description=str(desc_path),
        file=str(function_file_path),
        permissions={
            "public": True,
            "authorized_ids": [],
        },
    )


@pytest.fixture
def data_sample_query(tmpdir):
    data_sample_dir_path = tmpdir / "data_sample_0"
    data_sample_file_path = data_sample_dir_path / "data.txt"
    data_sample_file_path.write_text("Hello world 0", encoding="utf-8", ensure=True)

    return {
        "path": str(data_sample_dir_path),
        "data_manager_keys": ["42"],
    }


@pytest.fixture
def data_samples_query(tmpdir):
    nb = 3
    paths = []
    for i in range(nb):
        data_sample_dir_path = tmpdir / f"data_sample_{i}"
        data_sample_file_path = data_sample_dir_path / "data.txt"
        data_sample_file_path.write_text(f"Hello world {i}", encoding="utf-8", ensure=True)

        paths.append(str(data_sample_dir_path))

    return {
        "paths": paths,
        "data_manager_keys": ["42"],
    }


@pytest.fixture(scope="session")
def asset_factory():
    return data_factory.AssetsFactory("test_debug")


@pytest.fixture()
def data_sample(asset_factory):
    return asset_factory.create_data_sample()


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
