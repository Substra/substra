import pathlib
import uuid

import pytest

from substra.sdk.schemas import DataSampleSpec


@pytest.mark.parametrize("path", [pathlib.Path() / "data", "./data", pathlib.Path().cwd() / "data"])
def test_datasample_spec_resolve_path(path):
    datasample_spec = DataSampleSpec(path=path, data_manager_keys=[str(uuid.uuid4())])

    assert datasample_spec.path == pathlib.Path().cwd() / "data"


def test_datasample_spec_resolve_paths():
    paths = [pathlib.Path() / "data", "./data", pathlib.Path().cwd() / "data"]
    datasample_spec = DataSampleSpec(paths=paths, data_manager_keys=[str(uuid.uuid4())])

    assert all([path == pathlib.Path().cwd() / "data" for path in datasample_spec.paths])


def test_datasample_spec_exclusive_path():
    with pytest.raises(ValueError):
        DataSampleSpec(paths=["fake_paths"], path="fake_paths", data_manager_keys=[str(uuid.uuid4())])


def test_datasample_spec_no_path():
    with pytest.raises(ValueError):
        DataSampleSpec(data_manager_keys=[str(uuid.uuid4())])


def test_datasample_spec_paths_set_to_none():
    with pytest.raises(ValueError):
        DataSampleSpec(paths=None, data_manager_keys=[str(uuid.uuid4())])


def test_datasample_spec_path_set_to_none():
    with pytest.raises(ValueError):
        DataSampleSpec(path=None, data_manager_keys=[str(uuid.uuid4())])
