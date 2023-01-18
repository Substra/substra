import pytest

from substra.sdk import models
from substra.sdk import schemas

from .. import datastore
from ..utils import mock_requests



def test_archive_dataset(client, mocker):
    archive_method = getattr(client, f"archive_dataset")
    get_method = getattr(client, f"get_dataset")

    item = getattr(datastore, "DATASET")
    archived_field = {"archived": True}
    archived_dataset = {**item, **archived_field}

    m_put = mock_requests(mocker, "put")
    m_get = mock_requests(mocker, "get", response=item)

    archive_method("magic-key", archived_field["archived"])
    response = get_method("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type("dataset")](**archived_dataset)
    m_put.assert_called()
    m_get.assert_called()
