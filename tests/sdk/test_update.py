from substra.sdk import models
from substra.sdk import schemas

from .. import datastore
from ..utils import mock_requests


def test_add_compute_plan_tuples(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.add_compute_plan_tuples("foo", {})

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called


def test_add_compute_plan_tuples_with_schema(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.add_compute_plan_tuples("foo", schemas.UpdateComputePlanSpec(key="foo"))

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called
