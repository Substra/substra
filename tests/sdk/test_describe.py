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

import pytest

import substra

from .. import datastore
from .utils import mock_response, mock_requests, mock_requests_responses


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'aggregate_algo', 'composite_algo', 'objective']
)
def test_describe_asset(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    responses = [
        mock_response(item),  # metadata
        mock_response('foo'),  # data
    ]
    m = mock_requests_responses(mocker, 'get', responses)

    method = getattr(client, f'describe_{asset_name}')
    response = method("magic-key")

    assert response == 'foo'
    m.assert_called()


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'aggregate_algo', 'composite_algo', 'objective']
)
def test_describe_asset_not_found(asset_name, client, mocker):
    m = mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method = getattr(client, f'describe_{asset_name}')
        method('foo')

    assert m.call_count == 1


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'aggregate_algo', 'composite_algo', 'objective']
)
def test_describe_description_not_found(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    responses = [
        mock_response(item),  # metadata
        mock_response('foo', 404),  # data
    ]
    m = mock_requests_responses(mocker, 'get', responses)

    method = getattr(client, f'describe_{asset_name}')

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method("key")

    assert m.call_count == 2
