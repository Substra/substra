import pytest
import yaml

from substra.sdk import exceptions
from substra.sdk import schemas
from substra.sdk.client import Client
from substra.sdk.client import _upper_slug
from substra.sdk.exceptions import ConfigurationInfoError


@pytest.fixture
def config_file(tmp_path):
    config_dict = {
        "toto": {
            "backend_type": "remote",
            "url": "toto-org.com",
            "username": "toto_file_username",
            "password": "toto_file_password",
        }
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_dict))
    return config_file


def stub_login(username, password):
    if username == "org-1" and password == "password1":
        return "token1"
    if username == "env_var_username" and password == "env_var_password":
        return "env_var_token"
    if username == "toto_file_username" and password == "toto_file_password":
        return "toto_file_token"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("toto", "TOTO"),
        ("client-org-1", "CLIENT_ORG_1"),
        ("un nom très français", "UN_NOM_TRES_FRANCAIS"),
    ],
)
def test_upper_slug(input, expected):
    assert expected == _upper_slug(input)


def test_default_client():
    client = Client()
    assert client.backend_mode == schemas.BackendType.LOCAL_SUBPROCESS


@pytest.mark.parametrize(
    ["mode", "client_name", "url", "token", "insecure", "retry_timeout"],
    [
        (schemas.BackendType.LOCAL_SUBPROCESS, "foo", None, None, True, 5),
        (schemas.BackendType.LOCAL_DOCKER, "foobar", None, None, True, None),
        (schemas.BackendType.REMOTE, "bar", "example.com", "bloop", False, 15),
        (schemas.BackendType.LOCAL_SUBPROCESS, "hybrid", "example.com", "foo", True, 500),
        (schemas.BackendType.REMOTE, "foofoo", "https://example.com/api-token-auth/", None, True, 500),
    ],
)
def test_client_configured_in_code(mode, client_name, url, token, insecure, retry_timeout):
    client = Client(
        backend_type=mode,
        client_name=client_name,
        url=url,
        token=token,
        insecure=insecure,
        retry_timeout=retry_timeout,
    )
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
    if url is not None:
        assert client._url == url
    else:
        assert client._url is None


def test_client_should_raise_when_missing_name():
    with pytest.raises(ConfigurationInfoError):
        Client(configuration_file="something")


def test_client_with_password(mocker):
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    rest_client_logout = mocker.patch("substra.sdk.backends.remote.rest_client.Client.logout")
    client_args = {
        "backend_type": "remote",
        "url": "example.com",
        "token": None,
        "username": "org-1",
        "password": "password1",
    }

    client = Client(**client_args)
    assert client._token == "token1"
    client.logout()
    assert client._token is None
    rest_client_logout.assert_called_once()
    del client

    rest_client_logout.reset_mock()
    client = Client(**client_args)
    del client
    rest_client_logout.assert_called_once()

    rest_client_logout.reset_mock()
    with Client(**client_args) as client:
        assert client._token == "token1"
    rest_client_logout.assert_called_once()


def test_client_token_supercedes_password(mocker):
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    client = Client(
        backend_type="remote",
        url="example.com",
        token="token0",
        username="org-1",
        password="password1",
    )
    assert client._token == "token0"


def test_client_configuration_from_env_var(mocker, monkeypatch):
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_TOTO_BACKEND_TYPE", "remote")
    monkeypatch.setenv("SUBSTRA_TOTO_URL", "toto-org.com")
    monkeypatch.setenv("SUBSTRA_TOTO_USERNAME", "env_var_username")
    monkeypatch.setenv("SUBSTRA_TOTO_PASSWORD", "env_var_password")
    monkeypatch.setenv("SUBSTRA_TOTO_RETRY_TIMEOUT", "42")
    monkeypatch.setenv("SUBSTRA_TOTO_INSECURE", "true")
    client = Client(client_name="toto")
    assert client.backend_mode == "remote"
    assert client._url == "toto-org.com"
    assert client._token == "env_var_token"
    assert client._retry_timeout == 42
    assert client._insecure is True


def test_client_configuration_from_config_file(mocker, config_file):
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    client = Client(configuration_file=config_file, client_name="toto")
    assert client.backend_mode == "remote"
    assert client._url == "toto-org.com"
    assert client._token == "toto_file_token"
    assert client._retry_timeout == 300
    assert client._insecure is False


def test_client_configuration_code_overrides_env_var(monkeypatch):
    """
    A variable set in the code overrides one set in an env variable
    """
    monkeypatch.setenv("SUBSTRA_TOTO_BACKEND_TYPE", "remote")
    monkeypatch.setenv("SUBSTRA_TOTO_URL", "toto-org.com")
    monkeypatch.setenv("SUBSTRA_TOTO_USERNAME", "env_var_username")
    monkeypatch.setenv("SUBSTRA_TOTO_PASSWORD", "env_var_password")
    monkeypatch.setenv("SUBSTRA_TOTO_RETRY_TIMEOUT", "42")
    monkeypatch.setenv("SUBSTRA_TOTO_INSECURE", "true")
    client = Client(
        client_name="toto",
        backend_type="subprocess",
        url="",
    )
    assert client.backend_mode == "subprocess"
    assert client._url == ""
    assert client._token is None
    assert client._retry_timeout == 42
    assert client._insecure is True


def test_client_configuration_code_overrides_config_file(mocker, config_file):
    """
    A variable set in the code overrides one set in a config file
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    client = Client(
        client_name="toto",
        configuration_file=config_file,
        username="org-1",
        password="password1",
        retry_timeout=100,
    )
    assert client.backend_mode == "remote"
    assert client._url == "toto-org.com"
    assert client._token == "token1"
    assert client._retry_timeout == 100
    assert client._insecure is False


def test_client_configuration_env_var_overrides_config_file(mocker, monkeypatch, config_file):
    """
    A variable set in an env var overrides one set in a config file
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_TOTO_BACKEND_TYPE", "docker")
    monkeypatch.setenv("SUBSTRA_TOTO_USERNAME", "env_var_username")
    monkeypatch.setenv("SUBSTRA_TOTO_PASSWORD", "env_var_password")
    client = Client(configuration_file=config_file, client_name="toto", retry_timeout=12)
    assert client.backend_mode == "docker"
    assert client._url == "toto-org.com"
    assert client._token == "env_var_token"
    assert client._retry_timeout == 12
    assert client._insecure is False


def test_login_remote_without_url(tmpdir):
    with pytest.raises(exceptions.SDKException):
        Client(backend_type="remote")


def test_client_configuration_configuration_file_path_from_env_var(mocker, monkeypatch, config_file):
    """
    The configuration file path can be set through an env var
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH", config_file)
    client = Client(client_name="toto")
    assert client.backend_mode == "remote"
    assert client._url == "toto-org.com"
    assert client._token == "toto_file_token"
    assert client._retry_timeout == 300
    assert client._insecure is False


def test_client_configuration_configuration_file_path_parameter_supercedes_env_var(
    mocker, monkeypatch, config_file, tmp_path
):
    """
    The configuration file path env var is supercedes by `configuration_file=`
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH", config_file)

    config_2_dict = {
        "toto": {
            "backend_type": "docker",
        }
    }
    config_2_file = tmp_path / "config.yaml"
    config_2_file.write_text(yaml.dump(config_2_dict))

    client = Client(configuration_file=config_2_file, client_name="toto")
    assert client.backend_mode == "docker"


def test_client_configuration_file_path_env_var_empty_string(mocker, monkeypatch, config_file):
    """
    The configuration file path env var is supercedes by `configuration_file=`
    """
    mocker.patch("substra.sdk.Client.login", side_effect=stub_login)
    monkeypatch.setenv("SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH", config_file)

    client = Client(configuration_file="", client_name="toto")
    assert client.backend_mode == "subprocess"
