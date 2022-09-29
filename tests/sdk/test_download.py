import os
from unittest.mock import patch

import pytest

import substra
from substra.sdk import Client

from .. import datastore
from ..utils import mock_requests
from ..utils import mock_requests_responses
from ..utils import mock_response


@pytest.mark.parametrize(
    "asset_type",
    [
        ("dataset"),
        ("algo"),
        ("model"),
    ],
)
def test_download_asset(asset_type, tmp_path, client, mocker):
    item = getattr(datastore, asset_type.upper())
    responses = [
        mock_response(item),  # metadata
        mock_response("foo"),  # data
    ]
    m = mock_requests_responses(mocker, "get", responses)

    method = getattr(client, f"download_{asset_type}")
    temp_file = method("foo", tmp_path)

    assert os.path.exists(temp_file)
    m.assert_called()


@pytest.mark.parametrize("asset_type", ["dataset", "algo", "model", "logs"])
def test_download_asset_not_found(asset_type, tmp_path, client, mocker):
    m = mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method = getattr(client, f"download_{asset_type}")
        method("foo", tmp_path)

    assert m.call_count == 1


@pytest.mark.parametrize("asset_type", ["dataset", "algo", "model"])
def test_download_content_not_found(asset_type, tmp_path, client, mocker):
    item = getattr(datastore, asset_type.upper())

    expected_call_count = 2
    responses = [
        mock_response(item),  # metadata
        mock_response("foo", status=404),  # description
    ]

    if asset_type == "model":
        responses = [responses[1]]  # No metadata for model download
        expected_call_count = 1

    m = mock_requests_responses(mocker, "get", responses)

    method = getattr(client, f"download_{asset_type}")

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method("key", tmp_path)

    assert m.call_count == expected_call_count


@pytest.mark.parametrize(
    "method_name, asset_type",
    [
        ("download_model_from_traintuple", "TRAINTUPLE"),
        ("download_model_from_aggregatetuple", "AGGREGATETUPLE"),
        ("download_head_model_from_composite_traintuple", "COMPOSITE_TRAINTUPLE"),
        ("download_trunk_model_from_composite_traintuple", "COMPOSITE_TRAINTUPLE"),
    ],
)
@patch.object(Client, "download_model")
def test_download_model_from_task(fake_download_model, tmp_path, client, method_name, asset_type, mocker):
    item = getattr(datastore, asset_type)
    responses = [
        mock_response(item),  # metadata
        mock_response("foo"),  # data
    ]

    m = mock_requests_responses(mocker, "get", responses)

    method = getattr(client, method_name)
    method("key", tmp_path)

    m.assert_called
    assert fake_download_model.call_count == 1


def test_download_logs(tmp_path, client, mocker):
    logs = b"Lorem ipsum dolor sit amet"
    tuple_key = "key"

    response = mock_response(logs)
    response.iter_content.return_value = [logs]

    m = mock_requests_responses(mocker, "get", [response])
    client.download_logs(tuple_key, tmp_path)

    m.assert_called_once()
    response.iter_content.assert_called_once()

    assert (tmp_path / f"tuple_logs_{tuple_key}.txt").read_bytes() == logs
