from .. import datastore
from .utils import mock_requests


def test_update_dataset(client, mocker):
    item = datastore.DATASET
    m = mock_requests(mocker, "post", response=item)

    response = client.update_dataset(
        'a key',
        {'objective_key': 'an another key', })

    assert response == item
    assert m.is_called()
