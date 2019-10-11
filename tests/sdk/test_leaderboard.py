import pytest
import substra

from .. import datastore
from .utils import mock_requests


def test_get_asset(client, mocker):
    item = datastore.OBJECTIVE
    method = getattr(client, 'leaderboard')

    m = mock_requests(mocker, "get", response=item)

    response = method("magic-key")

    assert response == item
    assert m.is_called()


def test_get_asset_not_found(client, mocker):
    mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        client.leaderboard("magic-key")
