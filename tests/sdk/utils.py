from unittest import mock

import requests


def mock_requests(mocker, method, response=None, status=200):

    def _req(*args, **kwargs):
        m = mock.MagicMock(spec=requests.Response)
        m.status_code = status
        m.json = mock.MagicMock(return_value=response)

        if status not in (200, 201):
            exception = requests.exceptions.HTTPError(str(status), response=m)
            m.raise_for_status = mock.MagicMock(side_effect=exception)

        return m

    return mocker.patch(
        f'substra.sdk.rest_client.requests.{method}',
        side_effect=_req,
    )
