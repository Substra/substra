from contextlib import nullcontext as does_not_raise

import pytest

from substra.sdk import exceptions
from substra.sdk.models import ComputePlanStatus
from substra.sdk.models import ComputeTaskStatus
from substra.sdk.models import TaskErrorType

from .. import datastore
from ..utils import mock_requests


def _param_name_maker(arg):
    if isinstance(arg, str):
        return arg
    else:
        return ""


@pytest.mark.parametrize(
    ("asset_dict", "function_name", "status", "expectation"),
    [
        (datastore.TRAINTASK, "wait_task", ComputeTaskStatus.done, does_not_raise()),
        (datastore.TRAINTASK, "wait_task", ComputeTaskStatus.canceled, pytest.raises(exceptions.FutureFailureError)),
        (datastore.COMPUTE_PLAN, "wait_compute_plan", ComputePlanStatus.done, does_not_raise()),
        (
            datastore.COMPUTE_PLAN,
            "wait_compute_plan",
            ComputePlanStatus.failed,
            pytest.raises(exceptions.FutureFailureError),
        ),
        (
            datastore.COMPUTE_PLAN,
            "wait_compute_plan",
            ComputePlanStatus.canceled,
            pytest.raises(exceptions.FutureFailureError),
        ),
    ],
    ids=_param_name_maker,
)
def test_wait(client, mocker, asset_dict, function_name, status, expectation):
    item = {**asset_dict, "status": status}
    mock_requests(mocker, "get", item)
    function = getattr(client, function_name)
    with expectation:
        function(key=item["key"])


def test_wait_task_failed(client, mocker):
    # We need an error type to stop the iteration
    item = {**datastore.TRAINTASK, "status": ComputeTaskStatus.failed, "error_type": TaskErrorType.internal}
    mock_requests(mocker, "get", item)
    with pytest.raises(exceptions.FutureFailureError):
        client.wait_task(key=item["key"])


@pytest.mark.parametrize(
    ("asset_dict", "function_name", "status"),
    [
        (datastore.TRAINTASK, "wait_task", ComputeTaskStatus.waiting_for_parent_tasks),
        (datastore.TRAINTASK, "wait_task", ComputeTaskStatus.waiting_for_builder_slot),
        (datastore.TRAINTASK, "wait_task", ComputeTaskStatus.waiting_for_executor_slot),
        (datastore.COMPUTE_PLAN, "wait_compute_plan", ComputePlanStatus.created),
    ],
    ids=_param_name_maker,
)
def test_wait_timeout(client, mocker, asset_dict, function_name, status):
    item = {**asset_dict, "status": status}
    mock_requests(mocker, "get", item)
    function = getattr(client, function_name)
    with pytest.raises(exceptions.FutureTimeoutError):
        # mock_requests returns only once and timeout=0 is falsy, so setting a microscopic duration
        function(key=item["key"], timeout=1e-10)
