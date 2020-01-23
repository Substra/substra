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

import pytest
import requests

from substra.sdk import rest_client, exceptions

from .utils import mock_response, mock_requests, mock_requests_responses


CONFIG = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': {
        'username': 'foo',
    },
    'insecure': False,
}

CONFIG_SECURE = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': {
        'username': 'foo',
    },
    'insecure': False,
}

CONFIG_INSECURE = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': {
        'username': 'foo',
    },
    'insecure': True,
}

CONFIGS = [CONFIG, CONFIG_SECURE, CONFIG_INSECURE]


@pytest.mark.parametrize("config", CONFIGS)
def test_post_success(mocker, config):
    m = mock_requests(mocker, "post", response={})
    rest_client.Client(config).add('http://foo', {})
    assert len(m.call_args_list) == 1


@pytest.mark.parametrize("status_code, http_response, sdk_exception", [
    (400, {"message": "Invalid Request"}, exceptions.InvalidRequest),

    (401, {"message": "Invalid username/password"}, exceptions.AuthenticationError),

    (403, {"message": "Unauthorized"}, exceptions.AuthorizationError),

    (404, {"message": "Not Found"}, exceptions.NotFound),

    (408, {"pkhash": "a-key"}, exceptions.RequestTimeout),
    (408, {}, exceptions.RequestTimeout),

    (409, {"pkhash": "a-key"}, exceptions.AlreadyExists),
    (409, {"pkhash": ["a-key", "other-key"]}, exceptions.AlreadyExists),

    (500, "CRASH", exceptions.InternalServerError),
])
def test_request_http_errors(mocker, status_code, http_response, sdk_exception):
    m = mock_requests(mocker, "post", response=http_response, status=status_code)
    with pytest.raises(sdk_exception):
        rest_client.Client(CONFIG).add('http://foo', {})
    assert len(m.call_args_list) == 1


def test_request_connection_error(mocker):
    mocker.patch('substra.sdk.rest_client.requests.post',
                 side_effect=requests.exceptions.ConnectionError)
    with pytest.raises(exceptions.ConnectionError):
        rest_client.Client(CONFIG).add('foo', {})


def test_add_timeout_with_retry(mocker):
    asset_name = "traintuple"
    responses = [
        mock_response(response={"pkhash": "a-key"}, status=408),
        mock_response(response={"pkhash": "a-key"}),
    ]
    m_post = mock_requests_responses(mocker, "post", responses)
    asset = rest_client.Client(CONFIG).add(asset_name, retry_timeout=60)
    assert len(m_post.call_args_list) == 2
    assert asset == {"pkhash": "a-key"}


def test_add_exist_ok(mocker):
    asset_name = "traintuple"
    m_post = mock_requests(mocker, "post", response={"pkhash": "a-key"}, status=409)
    m_get = mock_requests(mocker, "get", response={"pkhash": "a-key"})
    asset = rest_client.Client(CONFIG).add(asset_name, exist_ok=True)
    assert len(m_post.call_args_list) == 1
    assert len(m_get.call_args_list) == 1
    assert asset == {"pkhash": "a-key"}
