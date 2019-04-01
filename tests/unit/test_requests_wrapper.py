from unittest import mock
import pytest

from substra_sdk_py import requests_wrapper

from .test_base import mock_success_response


def mocked_requests_post_success(*args, **kwargs):
    return mock_success_response()


CONFIG = {
    'url': 'http://toto.com',
    'version': '1.0',
    'auth': False,
    'insecure': False,
}

CONFIG_SECURE = {
    'url': 'http://toto.com',
    'version': '1.0',
    'auth': {
        'user': 'foo',
        'password': 'bar',
    },
    'insecure': False,
}

CONFIG_INSECURE = {
    'url': 'http://toto.com',
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
    with mock.patch('substra_sdk_py.requests_wrapper.requests.post',
                    side_effect=mocked_requests_post_success) as mocked:
        requests_wrapper.post(config, 'http://toto', {})
    assert len(mocked.call_args_list) == 1
