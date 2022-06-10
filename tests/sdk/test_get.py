# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        "metric",
        "model",
        "dataset",
        "data_sample",
        "algo",
        "testtuple",
        "traintuple",
        "aggregatetuple",
        "composite_traintuple",
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


def test_get_asset_not_found(client, mocker):
    mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        client.get_dataset("magic-key")


@pytest.mark.parametrize(
    "asset_type",
    [
        "metric",
        "dataset",
        "algo",
        "testtuple",
        "traintuple",
        "aggregatetuple",
        "composite_traintuple",
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


def test_get_logs(client, mocker):
    logs = "Lorem ipsum dolor sit amet"
    tuple_key = "key"

    responses = [mock_response(logs)]
    m = mock_requests_responses(mocker, "get", responses)
    result = client.get_logs(tuple_key)

    m.assert_called_once()
    assert result == logs


def test_get_performances(client, mocker):
    """Test the get_performances features, and test the immediate conversion to pandas DataFrame."""
    cp_item = datastore.COMPUTE_PLAN
    perf_item = datastore.COMPUTE_PLAN_PERF

    m = mock_requests_responses(mocker, "get", [mock_response(cp_item), mock_response(perf_item)])

    response = client.get_performances("magic-key")

    df = pd.DataFrame(response.dict())
    assert list(df.columns) == list(response.dict().keys())
    assert df.shape[0] == perf_item["count"]
    assert m.call_count == 2
