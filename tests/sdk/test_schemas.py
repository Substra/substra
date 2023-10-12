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
