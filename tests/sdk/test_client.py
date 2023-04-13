import pytest

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
    # assert client.backend_mode == schemas.BackendType.LOCAL_SUBPROCESS
    # assert client._backend._client.token == token if token is not None
