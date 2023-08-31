import pandas as pd
import pytest

import substra
from substra.sdk import models
from substra.sdk import schemas

from .. import datastore
from ..utils import mock_requests
from ..utils import mock_requests_responses
from ..utils import mock_response


@pytest.mark.parametrize(
    "asset_type",
    [
        "model",
        "dataset",
        "data_sample",
        "function",
        "compute_plan",
    ],
)
def test_get_asset(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())
    method = getattr(client, f"get_{asset_type}")

    m = mock_requests(mocker, "get", response=item)

    response = method("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type(asset_type)](**item)
    m.assert_called()


@pytest.mark.parametrize(
    "asset_type",
    [
        "predicttask",
        "testtask",
        "traintask",
        "aggregatetask",
        "composite_traintask",
    ],
)
def test_get_task(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())

    m = mock_requests(mocker, "get", response=item)

    response = client.get_task("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type.Task](**item)
    m.assert_called()


def test_get_asset_not_found(client, mocker):
    mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        client.get_dataset("magic-key")


@pytest.mark.parametrize(
    "asset_type",
    [
        "dataset",
        "function",
        "compute_plan",
        "model",
    ],
)
def test_get_extra_field(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())
    raw = getattr(datastore, asset_type.upper()).copy()
    raw["unknown_extra_field"] = "some value"

    method = getattr(client, f"get_{asset_type}")

    m = mock_requests(mocker, "get", response=raw)

    response = method("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type(asset_type)](**item)
    m.assert_called()


@pytest.mark.parametrize(
    "asset_type",
    [
        "predicttask",
        "testtask",
        "traintask",
        "aggregatetask",
        "composite_traintask",
    ],
)
def test_get_task_extra_field(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())
    raw = getattr(datastore, asset_type.upper()).copy()
    raw["unknown_extra_field"] = "some value"

    m = mock_requests(mocker, "get", response=raw)

    response = client.get_task("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type.Task](**item)
    m.assert_called()


def test_get_logs(client, mocker):
    logs = "Lorem ipsum dolor sit amet"
    task_key = "key"

    responses = [mock_response(logs)]
    m = mock_requests_responses(mocker, "get", responses)
    result = client.get_logs(task_key)

    m.assert_called_once()
    assert result == logs


def test_get_performances(client, mocker):
    """Test the get_performances features, and test the immediate conversion to pandas DataFrame."""
    cp_item = datastore.COMPUTE_PLAN
    perf_item = datastore.COMPUTE_PLAN_PERF

    m = mock_requests_responses(mocker, "get", [mock_response(cp_item), mock_response(perf_item)])

    response = client.get_performances("magic-key")
    results = response.model_dump()

    df = pd.DataFrame(results)
    assert list(df.columns) == list(results.keys())
    assert all(len(v) == df.shape[0] for v in results.values())
    assert m.call_count == 2
