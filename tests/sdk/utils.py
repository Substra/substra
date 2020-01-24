# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

import requests


def mock_response(response=None, status=200, headers=None):
    headers = headers or {}
    m = mock.MagicMock(spec=requests.Response)
    m.status_code = status
    m.headers = headers
    m.text = str(response)
    m.json = mock.MagicMock(return_value=response, headers=headers)

    if status not in (200, 201):
        exception = requests.exceptions.HTTPError(str(status), response=m)
        m.raise_for_status = mock.MagicMock(side_effect=exception)

    return m


def mock_requests_responses(mocker, method, responses):
    return mocker.patch(
        f'substra.sdk.rest_client.requests.{method}',
        side_effect=responses,
    )


def mock_requests(mocker, method, response=None, status=200, headers=None):
    r = mock_response(response, status, headers)
    return mock_requests_responses(mocker, method, (r, ))
