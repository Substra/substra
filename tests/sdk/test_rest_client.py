import pytest

from substra.sdk import rest_client

from .utils import mock_requests


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
def test_post_success(mocker, config):
    m = mock_requests(mocker, "post")
    rest_client.Client(config).add('http://foo', {})
    assert len(m.call_args_list) == 1
