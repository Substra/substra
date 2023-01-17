import pytest

import substra
from substra.sdk.schemas import AlgoSpec

from . import data_factory
from .fl_interface import FLAlgoInputs
from .fl_interface import FLAlgoOutputs
from .fl_interface import AlgoCategory


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )


@pytest.fixture
def client(tmpdir):
    c = substra.Client(url="http://foo.io")
    return c


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-cli"
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
        "type": "images",
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
def algo_query(tmpdir):
    algo_file_path = tmpdir / "algo.tar.gz"
    algo_file_path.write(b"tar gz archive")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    algo_category = AlgoCategory.simple

    return AlgoSpec(
        name="algo_name",
        inputs=FLAlgoInputs[algo_category],
        outputs=FLAlgoOutputs[algo_category],
        description=str(desc_path),
        file=str(algo_file_path),
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
