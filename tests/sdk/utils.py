from unittest import mock

import requests


def mock_requests_response(response=None, status=200, headers=None):
    m = mock.MagicMock(spec=requests.Response)
    m.status_code = status
    m.headers = headers
    m.text = str(response)
    m.json = mock.MagicMock(return_value=response, headers=headers)

    if status not in (200, 201):
        exception = requests.exceptions.HTTPError(str(status), response=m)
        m.raise_for_status = mock.MagicMock(side_effect=exception)

    return m


def mock_requests(mocker, method, response=None, status=200, headers=None):

    def _req(*args, **kwargs):
        return mock_requests_response(response, status, headers)

    return mocker.patch(
        f'substra.sdk.rest_client.requests.{method}',
        side_effect=_req,
    )
