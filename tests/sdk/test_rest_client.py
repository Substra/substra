import json

import pytest
import requests

from substra.sdk import exceptions
from substra.sdk.backends.remote import rest_client
from substra.sdk.client import Client

from .. import datastore
from ..utils import mock_requests
from ..utils import mock_requests_responses
from ..utils import mock_response

CONFIG = {
    "url": "http://foo.com",
    "insecure": False,
}

CONFIG_SECURE = {
    "url": "http://foo.com",
    "insecure": False,
}

CONFIG_INSECURE = {
    "url": "http://foo.com",
    "insecure": True,
}

CONFIGS = [CONFIG, CONFIG_SECURE, CONFIG_INSECURE]


def _client_from_config(config):
    return rest_client.Client(
        config["url"],
        config["insecure"],
        None,
    )


@pytest.mark.parametrize("config", CONFIGS)
def test_post_success(mocker, config):
    m = mock_requests(mocker, "post", response={})
    _client_from_config(config).add("http://foo", {})
    assert len(m.call_args_list) == 1


@pytest.mark.parametrize("config", CONFIGS)
def test_verify_login(mocker, config):
    """
    check "insecure" configuration results in endpoints being called with verify=False
    """
    m_post = mock_requests(mocker, "post", response={"id": "a", "token": "a", "expires_at": "3000-01-01T00:00:00Z"})
    m_delete = mock_requests(mocker, "delete", response={})

    c = _client_from_config(config)
    c.login("foo", "bar")
    c.logout()
    if config.get("insecure", None):
        assert m_post.call_args.kwargs["verify"] is False
        assert m_delete.call_args.kwargs["verify"] is False
    else:
        assert "verify" not in m_post.call_args.kwargs or m_post.call_args.kwargs["verify"]
        assert "verify" not in m_post.call_args.kwargs or m_delete.call_args.kwargs["verify"]


@pytest.mark.parametrize(
    "status_code, http_response, sdk_exception",
    [
        (400, {"detail": "Invalid Request"}, exceptions.InvalidRequest),
        (401, {"detail": "Invalid username/password"}, exceptions.AuthenticationError),
        (403, {"detail": "Unauthorized"}, exceptions.AuthorizationError),
        (404, {"detail": "Not Found"}, exceptions.NotFound),
        (408, {"key": "a-key"}, exceptions.RequestTimeout),
        (408, {}, exceptions.RequestTimeout),
        (500, "CRASH", exceptions.InternalServerError),
    ],
)
def test_request_http_errors(mocker, status_code, http_response, sdk_exception):
    m = mock_requests(mocker, "post", response=http_response, status=status_code)
    with pytest.raises(sdk_exception):
        _client_from_config(CONFIG).add("http://foo", {})
    assert len(m.call_args_list) == 1


def test_request_connection_error(mocker):
    mocker.patch(
        "substra.sdk.backends.remote.rest_client.requests.post", side_effect=requests.exceptions.ConnectionError
    )
    with pytest.raises(exceptions.ConnectionError):
        _client_from_config(CONFIG).add("foo", {})


def test_add_timeout_with_retry(mocker):
    asset_type = "traintask"
    responses = [
        mock_response(response={"key": "a-key"}, status=408),
        mock_response(response={"key": "a-key"}),
    ]
    m_post = mock_requests_responses(mocker, "post", responses)
    asset = _client_from_config(CONFIG).add(asset_type, retry_timeout=60)
    assert len(m_post.call_args_list) == 2
    assert asset == {"key": "a-key"}


def test_add_already_exist(mocker):
    asset_type = "traintask"
    m_post = mock_requests(mocker, "post", response={"key": "a-key"}, status=409)
    asset = _client_from_config(CONFIG).add(asset_type)
    assert len(m_post.call_args_list) == 1
    assert asset == {"key": "a-key"}


def test_add_wrong_url(mocker):
    """Check correct error is raised when wrong url with correct syntax is set."""
    error = json.decoder.JSONDecodeError("", "", 0)

    mock_requests(mocker, "post", status=200, json_error=error)
    test_client = Client(url="http://www.dummy.com", token="foo")
    with pytest.raises(exceptions.BadConfiguration) as e:
        test_client.login("test_client", "hehe")
    assert "Make sure that given url" in e.value.args[0]


def test_list_paginated(mocker):
    asset_type = "traintask"
    items = [datastore.TRAINTASK, datastore.TRAINTASK]
    responses = [
        mock_response(
            response={
                "count": len(items),
                "next": "http://foo.com/?page=2",
                "previous": None,
                "results": items[:1],
            },
            status=200,
        ),
        mock_response(
            response={
                "count": len(items),
                "next": None,
                "previous": "http://foo.com/?page=1",
                "results": items[1:],
            },
            status=200,
        ),
    ]
    m_get = mock_requests_responses(mocker, "get", responses)
    asset = _client_from_config(CONFIG).list(asset_type)
    assert len(asset) == len(items)
    assert len(m_get.call_args_list) == 2


def test_list_not_paginated(mocker):
    asset_type = "traintask"
    items = [datastore.TRAINTASK, datastore.TRAINTASK]
    m_get = mock_requests(
        mocker,
        "get",
        response={
            "count": len(items),
            "next": "http://foo.com/?page=2",
            "previous": None,
            "results": items[:1],
        },
        status=200,
    )
    asset = _client_from_config(CONFIG).list(asset_type, paginated=False)
    assert len(asset) != len(items)
    assert len(m_get.call_args_list) == 1
