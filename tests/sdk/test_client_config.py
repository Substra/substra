import json

import pytest

from substra.sdk import Client
from .utils import mock_requests


@pytest.fixture(params=[
    None,  # files won't be created
    '{}',  # files will be created but contain an empty json
])
def non_existing_or_empty_config_paths(tmpdir, request):
    config_path = tmpdir / 'substra.json'
    tokens_path = tmpdir / 'substra-tokens.json'
    if request.param:
        config_path.write_text(request.param, 'utf-8')
        tokens_path.write_text(request.param, 'utf-8')
    return config_path


@pytest.fixture
def default_config_paths(tmpdir):
    config_path = tmpdir / 'substra.json'
    tokens_path = tmpdir / 'substra-tokens.json'
    config_path.write_text(json.dumps({
        'tokens_path': str(tokens_path),
        'profiles': {
            'default': {
                'url': 'http://default.example.com',
                'secure': False,
                'version': '0.0',
            },
        },
    }), 'utf-8')
    tokens_path.write_text(json.dumps({
        'default': 'default token',
    }), 'utf-8')

    return config_path


@pytest.fixture
def foo_config_paths(tmpdir):
    config_path = tmpdir / 'substra.json'
    tokens_path = tmpdir / 'substra-tokens.json'
    config_path.write_text(json.dumps({
        'tokens_path': str(tokens_path),
        'profiles': {
            'foo': {
                'url': 'http://foo.example.com',
                'secure': False,
                'version': '0.0',
            },
        },
    }), 'utf-8')
    tokens_path.write_text(json.dumps({
        'foo': 'foo token'
    }), 'utf-8')

    return config_path


def test_non_existing_or_empty_config_paths(non_existing_or_empty_config_paths, mocker):
    client = Client(non_existing_or_empty_config_paths)
    assert not client.client._default_kwargs
    assert not client.client._base_url
    assert not client.client._headers

    client.add_profile('foo', 'http://foo.example.com', insecure=True)
    assert client.client._default_kwargs
    assert client.client._base_url
    assert 'Accept' in client.client._headers
    assert 'Authorization' not in client.client._headers

    m_post = mock_requests(mocker, "post", response={'token': 'foo'})
    client.login('foo', 'bar')
    m_post.assert_called()
    assert 'Authorization' in client.client._headers


def test_default_config_paths(default_config_paths, mocker):
    client = Client(default_config_paths)
    assert client.client._base_url == 'http://default.example.com'
    assert 'Accept' in client.client._headers
    assert 'Authorization' in client.client._headers

    client.add_profile('foo', 'http://foo.example.com')
    assert client.client._base_url == 'http://foo.example.com'
    assert 'Accept' in client.client._headers
    assert 'Authorization' not in client.client._headers

    m_post = mock_requests(mocker, "post", response={'token': 'foo'})
    client.login('foo', 'bar')
    m_post.assert_called()
    assert 'Authorization' in client.client._headers


def test_foo_config_paths(foo_config_paths, mocker):
    client = Client(foo_config_paths)
    assert not client.client._default_kwargs
    assert not client.client._base_url
    assert not client.client._headers

    client = Client(foo_config_paths, profile_name='foo')
    assert client.client._base_url == 'http://foo.example.com'
    assert 'Accept' in client.client._headers
    assert 'Authorization' in client.client._headers
