import pytest
import yaml

from substra.sdk import schemas
from substra.sdk.client import Client


@pytest.fixture
def dummy_rest_client():
    class DummyRestClient:
        def __init__(self, url):
            self.url = url

        def login(self, username, password):
            if self.url == "example1.com":
                return "token1"
            if self.url == "example2.com":
                return "token2"
            if self.url == "example3.com":
                return "token3"

    def get_rest_client(url):
        return DummyRestClient(url)

    return get_rest_client


def test_default_client():
    client = Client()
    assert client.backend_mode == schemas.BackendType.LOCAL_SUBPROCESS
    assert client.name is not None


@pytest.mark.parametrize(
    ["mode", "name", "url", "token", "insecure", "retry_timeout"],
    [
        ("subprocess", "foo", None, None, True, 5),
        ("docker", "foobar", None, None, True, None),
        ("remote", "bar", "example.com", "bloop", False, 15),
    ],
)
def test_client_configured_in_code(mode, name, url, token, insecure, retry_timeout):
    client = Client(backend_type=mode, name=name, url=url, token=token, insecure=insecure, retry_timeout=retry_timeout)
    assert client.name == name
    assert client.backend_mode == mode
    assert client._insecure == insecure
    if retry_timeout is not None:
        assert client._retry_timeout == retry_timeout
    else:
        assert client._retry_timeout == 300
    if token is not None:
        assert client._token == token
    else:
        assert client._token is None


def stub_login(username, password):
    if username == "org-1" and password == "password1":
        return "token1"
    if username == "env_var_username" and password == "env_var_password":
        return "env_var_token"
    if username == "org-3" and password == "toto_file_password":
        return "toto_file_username"


def test_client_with_password(mocker):
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    client = Client(
        backend_type="remote", name="toto", url="example.com", token=None, username="org-1", password="password1"
    )
    assert client._token == "token1"


@pytest.fixture
def config_file(tmp_path):
    config_dict = {
        "toto": {
            "url": "toto-org.com",
            "username": "toto_file_username",
            "password": "toto_file_password",
        }
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_dict))
    return config_file


def test_client_config_env_overrides_config_file(mocker, monkeypatch, config_file):
    """
    A variable set in an env var overrides one set in a config file
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_TOTO_USERNAME", "env_var_username")
    monkeypatch.setenv("SUBSTRA_TOTO_PASSWORD", "env_var_password")
    client = Client(
        configuration_file=config_file,
        backend_type="remote",
        name="toto",
        url=None,
        token=None,
    )
    assert client._url == "toto-org.com"
    assert client._token == "env_var_token"
