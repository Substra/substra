import pytest

from substra.sdk import models
from substra.sdk import schemas

from .. import datastore
from ..utils import mock_requests


@pytest.mark.parametrize(
    "asset_type",
    ["dataset", "function", "compute_plan"],
)
def test_update_asset(asset_type, client, mocker):
    update_method = getattr(client, f"update_{asset_type}")
    get_method = getattr(client, f"get_{asset_type}")

    item = getattr(datastore, asset_type.upper())
    name_update = {"name": "New name"}
    updated_item = {**item, **name_update}

    m_put = mock_requests(mocker, "put")
    m_get = mock_requests(mocker, "get", response=updated_item)

    update_method("magic-key", name_update["name"])
    response = get_method("magic-key")

    assert response == models.SCHEMA_TO_MODEL[schemas.Type(asset_type)](**updated_item)
    m_put.assert_called()
    m_get.assert_called()


def test_add_compute_plan_tasks(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.add_compute_plan_tasks("foo", {})

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called


def test_add_compute_plan_tasks_with_schema(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.add_compute_plan_tasks("foo", schemas.UpdateComputePlanTasksSpec(key="foo"))

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called
