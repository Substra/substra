from tests.utils import mock_requests


def cancel_compute_plan(mocker):
    m = mock_requests(mocker, "post", response=None)
    return m
