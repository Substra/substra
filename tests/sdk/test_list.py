import pytest

from .. import datastore
from .utils import mock_requests


@pytest.mark.parametrize(
    'asset_name', ['objective', 'dataset', 'algo', 'testtuple', 'traintuple']
)
def test_list_asset(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    method = getattr(client, f'list_{asset_name}')

    m = mock_requests(mocker, "get", response=[item])

    response = method()

    assert response == [item]
    assert m.is_called()


def test_list_asset_flatten(client, mocker):
    items = [datastore.ALGO]
    m = mock_requests(mocker, "get", response=[items])

    response = client.list_algo()

    assert response == items
    assert m.is_called()


def test_list_asset_with_filters(client, mocker):
    items = [datastore.ALGO]
    m = mock_requests(mocker, "get", response=[items])

    filters = ["algo:name:ABC", "OR", "data_manager:name:EFG"]
    response = client.list_algo(filters)

    assert response == items
    assert m.is_called()


def test_list_asset_with_filters_failure(client, mocker):
    items = [datastore.ALGO]
    m = mock_requests(mocker, "get", response=[items])

    filters = 'foo'
    with pytest.raises(ValueError) as exc_info:
        client.list_algo(filters)

    assert m.is_called()
    assert str(exc_info.value).startswith("Cannot load filters")
