import pytest
import substra

from .. import datastore
from .utils import mock_requests


def test_leaderboard(client, mocker):
    item = datastore.LEADERBOARD

    m = mock_requests(mocker, "get", response=item)

    response = client.leaderboard("magic-key")

    assert response == item
    assert m.is_called()


def test_leaderboard_not_found(client, mocker):
    mock_requests(mocker, "get", status=404)

    with pytest.raises(substra.sdk.exceptions.NotFound):
        client.leaderboard("magic-key")
