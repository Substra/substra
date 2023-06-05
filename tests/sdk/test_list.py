import pytest

from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas

from .. import datastore
from ..utils import make_paginated_response
from ..utils import mock_requests


@pytest.mark.parametrize(
    "asset_type",
    [
        "dataset",
        "function",
        "compute_plan",
        "data_sample",
        "model",
    ],
)
def test_list_asset(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())
    method = getattr(client, f"list_{asset_type}")

    mocked_response = make_paginated_response([item])
    m = mock_requests(mocker, "get", response=mocked_response)

    response = method()

    assert response == [models.SCHEMA_TO_MODEL[schemas.Type(asset_type)](**item)]
    m.assert_called()


@pytest.mark.parametrize(
    "asset_type",
    [
        "predicttask",
        "testtask",
        "traintask",
        "aggregatetask",
        "composite_traintask",
    ],
)
def test_list_task(asset_type, client, mocker):
    item = getattr(datastore, asset_type.upper())

    mocked_response = make_paginated_response([item])
    m = mock_requests(mocker, "get", response=mocked_response)

    response = client.list_task()

    assert response == [models.Task(**item)]
    m.assert_called()


@pytest.mark.parametrize(
    "asset_type,filters",
    [
        ("dataset", {"permissions": ["foo", "bar"]}),
        ("function", {"owner": ["foo", "bar"]}),
        ("compute_plan", {"name": "foo"}),
        ("compute_plan", {"status": [models.ComputePlanStatus.done.value]}),
        ("model", {"owner": ["MyOrg1MSP"]}),
    ],
)
def test_list_asset_with_filters(asset_type, filters, client, mocker):
    item = getattr(datastore, asset_type.upper())
    method = getattr(client, f"list_{asset_type}")

    mocked_response = make_paginated_response([item])
    m = mock_requests(mocker, "get", response=mocked_response)

    response = method(filters)

    assert response == [models.SCHEMA_TO_MODEL[schemas.Type(asset_type)](**item)]
    m.assert_called()


@pytest.mark.parametrize(
    "filters",
    [
        {"rank": [1, 3]},
        {"key": ["foo", "bar"]},
        {"worker": ["foo", "bar"]},
        {"owner": ["foo", "bar"]},
    ],
)
def test_list_task_with_filters(filters, client, mocker):
    items = datastore.TASK_LIST

    mocked_response = make_paginated_response(items)
    m = mock_requests(mocker, "get", response=mocked_response)

    response = client.list_task(filters)

    assert response == [models.Task(**item) for item in items]
    m.assert_called()


def test_list_asset_with_filters_failure(client, mocker):
    items = [datastore.FUNCTION]
    m = mock_requests(mocker, "get", response=items)

    filters = {"foo"}
    with pytest.raises(exceptions.FilterFormatError) as exc_info:
        client.list_function(filters)

    m.assert_not_called()
    assert str(exc_info.value).startswith("Cannot load filters")


def test_list_compute_plan_with_ordering(client, mocker):
    item = datastore.COMPUTE_PLAN

    mocked_response = make_paginated_response([item])
    m = mock_requests(mocker, "get", response=mocked_response)

    order_by = "start_date"
    response = client.list_compute_plan(order_by=order_by)

    assert response == [models.SCHEMA_TO_MODEL[schemas.Type.ComputePlan](**item)]
    m.assert_called()


def test_list_task_with_ordering(client, mocker):
    items = datastore.TASK_LIST

    mocked_response = make_paginated_response(items)
    m = mock_requests(mocker, "get", response=mocked_response)

    order_by = "start_date"
    response = client.list_task(order_by=order_by)

    assert response == [models.Task(**item) for item in items]
    m.assert_called()


def test_list_asset_with_ordering_failure(client, mocker):
    items = [datastore.COMPUTE_PLAN]
    m = mock_requests(mocker, "get", response=items)

    order_by = "foo"
    with pytest.raises(exceptions.OrderingFormatError) as exc_info:
        client.list_compute_plan(order_by=order_by)

    m.assert_not_called()
    assert str(exc_info.value).startswith("Please review the documentation")
