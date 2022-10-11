import json
import sys
import traceback
from unittest import mock

import click
import pytest
from click.testing import CliRunner

import substra
from substra.cli.interface import cli
from substra.cli.interface import error_printer


def execute(command, exit_code=0):
    runner = CliRunner()
    result = runner.invoke(cli, command)
    if exit_code == 0 and result.exit_code != 0 and result.exc_info:
        # if the test was supposed to succeed but failed,
        # we display the exception and the full traceback
        _, _, tb = result.exc_info
        traceback.print_tb(tb, file=sys.stdout)
        pytest.fail(str(result.exception))
    assert result.exit_code == exit_code, result.output
    return result.output


def client_execute(directory, command, exit_code=0):
    # force using a new config file and a new profile
    if "--config" not in command:
        cfgpath = directory / "substra.cfg"
        manager = substra.sdk.config.ConfigManager(str(cfgpath))
        manager.set_profile("default", url="http://foo")
        manager.save()
        command.extend(["--config", str(cfgpath)])
    return execute(command, exit_code=exit_code)


def test_command_help():
    output = execute(["--help"])
    assert "Usage:" in output


def test_command_version():
    output = execute(["--version"])
    assert substra.__version__ in output


def test_command_config(workdir):
    cfgfile = workdir / "cli.cfg"

    assert cfgfile.exists() is False

    new_url = "http://foo"
    new_profile = "foo"
    execute(
        [
            "config",
            new_url,
            "--profile",
            new_profile,
            "--config",
            str(cfgfile),
        ]
    )
    assert cfgfile.exists()

    # check new profile has been created, check also that default profile
    # has been created
    with cfgfile.open() as fp:
        cfg = json.load(fp)
    expected_profiles = ["foo"]
    assert list(cfg.keys()) == expected_profiles


def mock_client_call(mocker, method_name, response="", side_effect=None):
    return mocker.patch(f"substra.cli.interface.Client.{method_name}", return_value=response, side_effect=side_effect)


def test_command_login(workdir, mocker):
    m = mock_client_call(mocker, "login")
    client_execute(workdir, ["login", "--username", "foo", "--password", "bar"])
    m.assert_called()


def test_command_cancel_compute_plan(workdir, mocker):
    m = mock_client_call(mocker, "cancel_compute_plan", None)
    client_execute(workdir, ["cancel", "compute_plan", "fakekey"])
    m.assert_called()


@pytest.mark.parametrize(
    "exception",
    [
        (substra.exceptions.RequestException("foo", 400)),
        (substra.exceptions.ConnectionError("foo", 400)),
        (substra.exceptions.InvalidResponse(None, "foo")),
        (substra.exceptions.LoadDataException("foo", 400)),
    ],
)
def test_error_printer(mocker, exception):
    @error_printer
    def foo():
        raise exception

    mock_click_context = mock.MagicMock()
    mock_click_context.obj.verbose = False

    mocker.patch("substra.cli.interface.click.get_current_context", return_value=mock_click_context)
    with pytest.raises(click.ClickException, match="foo"):
        foo()
