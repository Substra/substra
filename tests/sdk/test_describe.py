import pytest

import substra

from .. import datastore
from .utils import mock_requests, mock_requests_response


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'objective']
)
def test_describe_asset(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    asset_response = mock_requests_response(item)

    description_response = mock_requests_response('foo')

    m = mocker.patch('substra.sdk.rest_client.requests.get',
                     side_effect=[asset_response, description_response])

    method = getattr(client, f'describe_{asset_name}')
    response = method("magic-key")

    assert response == 'foo'
    assert m.is_called()


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'objective']
)
def test_describe_asset_not_found(asset_name, client, mocker):
    m = mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method = getattr(client, f'describe_{asset_name}')
        method('foo')

    assert m.call_count == 1


@pytest.mark.parametrize(
    'asset_name', ['dataset', 'algo', 'objective']
)
def test_describe_description_not_found(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    asset_response = mock_requests_response(item)

    description_response = mock_requests_response('foo', 404)

    m = mocker.patch('substra.sdk.rest_client.requests.get',
                     side_effect=[asset_response, description_response])

    method = getattr(client, f'describe_{asset_name}')

    with pytest.raises(substra.sdk.exceptions.NotFound):
        method("key")

    assert m.call_count == 2
