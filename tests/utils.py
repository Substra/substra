from unittest import mock

import requests


def mock_response(response=None, status=200, headers=None, json_error=None):
    headers = headers or {}
    m = mock.MagicMock(spec=requests.Response)
    m.status_code = status
    m.headers = headers
    m.text = str(response)
    m.json = mock.MagicMock(return_value=response, headers=headers, side_effect=json_error)

    if status not in (200, 201):
        exception = requests.exceptions.HTTPError(str(status), response=m)
        m.raise_for_status = mock.MagicMock(side_effect=exception)

    return m


def mock_requests_responses(mocker, method, responses):
    return mocker.patch(
        f"substra.sdk.backends.remote.rest_client.requests.{method}",
        side_effect=responses,
    )


def mock_requests(mocker, method, response=None, status=200, headers=None, json_error=None):
    r = mock_response(response, status, headers, json_error)
    return mock_requests_responses(mocker, method, (r,))


def make_paginated_response(items):
    return {"count": len(items), "next": None, "previous": None, "results": items}
