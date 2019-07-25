from unittest import mock
import pytest

from substra.sdk import rest_client

from .test_base import mock_success_response


def mocked_requests_post_success(*args, **kwargs):
    return mock_success_response()


CONFIG = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': False,
    'insecure': False,
}

CONFIG_SECURE = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': {
        'user': 'foo',
        'password': 'bar',
    },
    'insecure': False,
}

CONFIG_INSECURE = {
    'url': 'http://foo.com',
    'version': '1.0',
    'auth': {
        'user': 'foo',
        'password': 'bar',
    },
    'insecure': True,
}

CONFIGS = [CONFIG, CONFIG_SECURE, CONFIG_INSECURE]


@pytest.mark.parametrize("config", CONFIGS)
def test_post_success(config):
    with mock.patch('substra.sdk.rest_client.requests.post',
                    side_effect=mocked_requests_post_success) as mocked:
        rest_client.Client(config).add('http://foo', {})
    assert len(mocked.call_args_list) == 1
