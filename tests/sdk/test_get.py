import pytest
import substra

from .. import datastore
from .utils import mock_requests


@pytest.mark.parametrize(
    'asset_name', ['objective', 'dataset', 'algo', 'testtuple', 'traintuple']
)
def test_get_asset(asset_name, client, mocker):
    item = getattr(datastore, asset_name.upper())
    method = getattr(client, f'get_{asset_name}')

    m = mock_requests(mocker, "get", response=item)

    response = method("magic-key")

    assert response == item
    assert m.is_called()


def test_get_asset_not_found(client, mocker):
    mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        client.get_dataset("magic-key")
