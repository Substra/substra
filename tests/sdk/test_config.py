import json

import pytest

import substra
import substra.sdk.config as configuration

DUMMY_CONFIG = {
    configuration.DEFAULT_PROFILE_NAME: {
        "url": "http://example.com",
        "insecure": configuration.DEFAULT_INSECURE,
    }
}

DUMMY_TOKENS = {
    configuration.DEFAULT_PROFILE_NAME: {
        "token": "foo",
    }
}


def test_add_from_config_file(tmpdir):
    path = tmpdir / "substra.cfg"
    manager_1 = configuration.ConfigManager(str(path))

    profile_1 = manager_1.set_profile("owkin", url="http://substra-backend.owkin.xyz:8000")
    manager_1.save()

    manager_2 = configuration.ConfigManager(str(path))
    profile_2 = manager_2.get_profile("owkin")
    assert profile_1 == profile_2


def test_add_from_config_file_from_file(tmpdir):
    path = tmpdir / "substra.cfg"
    conf = {
        "organization-1": {
            "insecure": False,
            "url": "http://substra-backend.org-1.com",
        },
    }

    path.write_text(json.dumps(conf), "UTF-8")
    manager = configuration.ConfigManager(str(path))
    profile = manager.get_profile("organization-1")

    assert conf["organization-1"] == profile


def test_add_load_bad_profile_from_file(tmpdir):
    path = tmpdir / "substra.cfg"
    conf = "organization-1"

    path.write_text(conf, "UTF-8")

    with pytest.raises(configuration.ConfigException):
        configuration.ConfigManager(str(path))


def test_from_config_file_fail(tmpdir):
    path = tmpdir / "substra.cfg"
    manager = configuration.ConfigManager(str(path))

    with pytest.raises(configuration.ConfigException):
        manager.get_profile("notfound")

    manager.set_profile("default", "foo", "bar")

    with pytest.raises(configuration.ProfileNotFoundError):
        manager.get_profile("notfound")


def test_login_remote_without_url(tmpdir):
    with pytest.raises(substra.exceptions.SDKException):
        substra.Client()


def test_token_without_tokens_path(tmpdir):
    config_path = tmpdir / "substra.json"
    config_path.write_text(json.dumps(DUMMY_CONFIG), "UTF-8")

    tokens_path = tmpdir / "substra-tokens.json"

    client = substra.Client.from_config_file(config_path=config_path, profile_name="default")
    assert client._token == ""

    client = substra.Client.from_config_file(
        config_path=config_path, tokens_path=tokens_path, profile_name="default", token="foo"
    )
    assert client._token == "foo"


def test_token_with_tokens_path(tmpdir):
    config_path = tmpdir / "substra.json"
    config_path.write_text(json.dumps(DUMMY_CONFIG), "UTF-8")

    tokens_path = tmpdir / "substra-tokens.json"
    tokens_path.write_text(json.dumps(DUMMY_TOKENS), "UTF-8")

    client = substra.Client.from_config_file(config_path=config_path, profile_name="default", tokens_path=tokens_path)
    assert client._token == "foo"

    client = substra.Client.from_config_file(
        config_path=config_path,
        profile_name="default",
        tokens_path=tokens_path,
        token="bar",
    )
    assert client._token == "bar"
