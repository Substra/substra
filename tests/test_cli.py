import json

from click.testing import CliRunner
import pytest

import substra
from substra.cli.interface import cli

from . import datastore


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-cli"
    d.mkdir()
    return d


def command_runner(command, exit_code=0):
    runner = CliRunner()
    result = runner.invoke(cli, command)
    assert result.exit_code == exit_code
    return result.output


def command_client_runner(tmpdir, command, exit_code=0):
    # force using a new config file and a new profile
    if '--config' not in command:
        cfgpath = tmpdir / 'substra.cfg'
        profile = {
            'url': 'http://toto',
            'version': '0.0',
            'insecure': False,
            'auth': False,
        }
        substra.config.add_profile(str(cfgpath), 'default', profile)
        command.extend(['--config', str(cfgpath)])
    return command_runner(command, exit_code=exit_code)


def test_command_help():
    output = command_runner(['--help'])
    assert 'Usage:' in output


def test_command_version():
    output = command_runner(['--version'])
    assert substra.__version__ in output


def test_command_config(workdir):
    cfgfile = workdir / "cli.cfg"

    assert cfgfile.exists() is False

    new_url = 'http://toto'
    new_profile = 'toto'
    command_runner([
        'config',
        new_url,
        '--profile', new_profile,
        '--config', str(cfgfile),
    ])
    assert cfgfile.exists()

    # check new profile has been created, check also that default profile
    # has been created
    with cfgfile.open() as fp:
        cfg = json.load(fp)
    expected_profiles = ['default', 'toto']
    assert list(cfg.keys()) == expected_profiles


@pytest.fixture
def mock_substra_list(mocker):
    response = [datastore.OBJECTIVE]
    with mocker.patch('substra.cli.interface.sb.Client.list',
                      return_value=response) as m:
        yield m


def test_command_list(workdir, mock_substra_list):
    output = command_client_runner(workdir, [
        'list', 'objective',
    ])
    assert datastore.OBJECTIVE['key'] in output


@pytest.fixture
def mock_substra_get(mocker):
    response = datastore.OBJECTIVE
    with mocker.patch('substra.cli.interface.sb.Client.get',
                      return_value=response) as m:
        yield m


def test_command_get(workdir, mock_substra_get):
    output = command_client_runner(workdir, [
        'get', 'objective', 'fakekey'
    ])
    assert datastore.OBJECTIVE['key'] in output
