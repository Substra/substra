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
import os

import substra

from .. import datastore
from .utils import mock_requests_responses, mock_requests, mock_response
from substra.sdk import Client, backends, schemas
from unittest.mock import patch


@pytest.mark.parametrize(
    'asset_name, filename', [
        ('dataset', 'opener.py'),
        ('algo', 'algo.tar.gz'),
        ('aggregate_algo', 'aggregate_algo.tar.gz'),
        ('composite_algo', 'composite_algo.tar.gz'),
        ('objective', 'metrics.py'),
        ('model', 'model_foo'),
    ]
)
def test_download_asset(asset_name, filename, tmp_path, client, mocker):
    item = getattr(datastore, asset_name.upper())
    responses = [
        mock_response(item),  # metadata
        mock_response('foo'),  # data
    ]
    m = mock_requests_responses(mocker, 'get', responses)

    method = getattr(client, f'download_{asset_name}')
    method("foo", tmp_path)

    temp_file = str(tmp_path) + '/' + filename
    assert os.path.exists(temp_file)
    m.assert_called()


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'aggregate_algo', 'composite_algo', 'objective', 'model']
)
def test_download_asset_not_found(asset_name, tmp_path, client, mocker):
    m = mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method = getattr(client, f'download_{asset_name}')
        method('foo', tmp_path)

    assert m.call_count == 1


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'aggregate_algo', 'composite_algo', 'objective', 'model']
)
def test_download_content_not_found(asset_name, tmp_path, client, mocker):
    item = getattr(datastore, asset_name.upper())

    expected_call_count = 2
    responses = [
        mock_response(item),  # metadata
        mock_response('foo', status=404),  # description
    ]

    if asset_name == 'model':
        responses = [responses[1]]  # No metadata for model download
        expected_call_count = 1

    m = mock_requests_responses(mocker, 'get', responses)

    method = getattr(client, f'download_{asset_name}')

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method("key", tmp_path)

    assert m.call_count == expected_call_count


@pytest.mark.parametrize(
    'method_name, expected_type', [
        ('download_model_from_traintuple', schemas.Type.Traintuple),
        ('download_model_from_aggregatetuple', schemas.Type.Aggregatetuple),
        ('download_head_model_from_composite_traintuple', schemas.Type.CompositeTraintuple),
        ('download_trunk_model_from_composite_traintuple', schemas.Type.CompositeTraintuple),
    ]
)
@patch.object(backends.Remote, 'get')
@patch.object(Client, 'download_model')
def test_download_model_from_tuple(
    fake_download_model,
    fake_get,
    tmp_path,
    client,
    method_name,
    expected_type
):
    method = getattr(client, method_name)
    method("key", tmp_path)

    assert fake_get.call_count == 1
    assert fake_get.call_args[0][0] is expected_type
    assert fake_download_model.call_count == 1
