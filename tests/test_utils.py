import os
import zipfile

import pytest

import substra
from substra.sdk import exceptions
from substra.sdk import schemas
from substra.sdk import utils


def _unzip(fp, destination):
    with zipfile.ZipFile(fp, "r") as zipf:
        zipf.extractall(destination)


def test_zip_folder(tmp_path):
    # initialise dir to zip
    dir_to_zip = tmp_path / "dir"
    dir_to_zip.mkdir()

    file_items = [
        ("name0.txt", "content0"),
        ("dir1/name1.txt", "content1"),
        ("dir2/name2.txt", "content2"),
    ]

    for name, content in file_items:
        path = dir_to_zip / name
        path.parents[0].mkdir(exist_ok=True)
        path.write_text(content)

    for name, _ in file_items:
        path = dir_to_zip / name
        assert os.path.exists(str(path))

    # zip dir
    fp = utils.zip_folder_in_memory(str(dir_to_zip))
    assert fp

    # unzip dir
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()
    _unzip(fp, str(destination_dir))
    for name, content in file_items:
        path = destination_dir / name
        assert os.path.exists(str(path))
        assert path.read_text() == content


@pytest.mark.parametrize(
    "filters,expected,exception",
    [
        ("str", None, exceptions.FilterFormatError),
        ({}, None, exceptions.FilterFormatError),
        (
            [{"key": "foo", "type": "bar", "value": "baz"}],
            None,
            exceptions.FilterFormatError,
        ),
        ([{"key": "foo", "type": "is", "value": "baz"}, {}], None, exceptions.FilterFormatError),
        ([{"key": "foo", "type": "is", "value": "baz"}], None, None),
    ],
)
def test_check_metadata_search_filter(filters, expected, exception):
    if exception:
        with pytest.raises(exception):
            utils._check_metadata_search_filters(filters)
    else:
        assert utils._check_metadata_search_filters(filters) == expected


@pytest.mark.parametrize(
    "asset_type,filters,expected,exception",
    [
        (
            schemas.Type.ComputePlan,
            {"status": [substra.models.ComputePlanStatus.doing.value]},
            {"status": [substra.models.ComputePlanStatus.doing.value]},
            None,
        ),
        (
            schemas.Type.Task,
            {"status": [substra.models.ComputeTaskStatus.done.value]},
            {"status": [substra.models.ComputeTaskStatus.done.value]},
            None,
        ),
        (schemas.Type.Task, {"rank": [1]}, {"rank": ["1"]}, None),
        (schemas.Type.DataSample, ["wrong filter type"], None, exceptions.FilterFormatError),
        (schemas.Type.ComputePlan, {"name": ["list"]}, None, exceptions.FilterFormatError),
        (schemas.Type.Task, {"foo": "not allowed key"}, None, exceptions.NotAllowedFilterError),
        (
            schemas.Type.ComputePlan,
            {"name": "cp1", "key": ["key1", "key2"]},
            {"name": "cp1", "key": ["key1", "key2"]},
            None,
        ),
    ],
)
def test_check_and_format_search_filters(asset_type, filters, expected, exception):
    if exception:
        with pytest.raises(exception):
            utils.check_and_format_search_filters(asset_type, filters)
    else:
        assert utils.check_and_format_search_filters(asset_type, filters) == expected


@pytest.mark.parametrize(
    "ordering, exception",
    [
        ("creation_date", None),
        ("start_date", None),
        ("foo", exceptions.OrderingFormatError),
        (None, None),
    ],
)
def test_check_search_ordering(ordering, exception):
    if exception:
        with pytest.raises(exception):
            utils.check_search_ordering(ordering)
    else:
        utils.check_search_ordering(ordering)
