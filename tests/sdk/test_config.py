import pytest
import yaml

import substra

DEFAULT_PROFILE_NAME = "default"

DUMMY_CONFIG = {
    DEFAULT_PROFILE_NAME: {
        "url": "http://example.com",
        "insecure": False,
    }
}

DUMMY_TOKENS = {
    DEFAULT_PROFILE_NAME: {
        "token": "foo",
    }
}


def test_login_remote_without_url(tmpdir):
    with pytest.raises(substra.exceptions.SDKException):
        substra.Client(backend_type="remote")


def test_token_without_tokens(tmpdir):
    config_path = tmpdir / "substra.yaml"
    config_path.write_text(yaml.dump(DUMMY_CONFIG), "UTF-8")

    client = substra.Client(configuration_file=config_path, client_name=DEFAULT_PROFILE_NAME)
    assert client._token is None

    config_path.write_text(yaml.dump(DUMMY_CONFIG), "UTF-8")

    client = substra.Client(configuration_file=config_path, client_name=DEFAULT_PROFILE_NAME, token="foo")
    assert client._token == "foo"


def test_token_with_tokens(tmpdir):
    config_path = tmpdir / "substra.yaml"
    config_path.write_text(yaml.dump(dict(DUMMY_CONFIG, **DUMMY_TOKENS)), "UTF-8")

    client = substra.Client(configuration_file=config_path, client_name=DEFAULT_PROFILE_NAME)
    assert client._token == "foo"

    client = substra.Client(
        configuration_file=config_path,
        client_name=DEFAULT_PROFILE_NAME,
        token="bar",
    )
    assert client._token == "bar"
