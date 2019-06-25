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


def execute(command, exit_code=0):
    runner = CliRunner()
    result = runner.invoke(cli, command)
    assert result.exit_code == exit_code
    return result.output


def client_execute(tmpdir, command, exit_code=0):
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
    return execute(command, exit_code=exit_code)


def test_command_help():
    output = execute(['--help'])
    assert 'Usage:' in output


def test_command_version():
    output = execute(['--version'])
    assert substra.__version__ in output


def test_command_config(workdir):
    cfgfile = workdir / "cli.cfg"

    assert cfgfile.exists() is False

    new_url = 'http://toto'
    new_profile = 'toto'
    execute([
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


def mock_client_call(mocker, method_name, response):
    return mocker.patch(f'substra.cli.interface.sb.Client.{method_name}',
                        return_value=response)


def test_command_list(workdir, mocker):
    response = [datastore.OBJECTIVE]
    with mock_client_call(mocker, 'list', response) as m:
        output = client_execute(workdir, [
            'list', 'objective',
        ])
    assert m.is_called()
    assert datastore.OBJECTIVE['key'] in output


def test_command_get(workdir, mocker):
    response = datastore.OBJECTIVE
    with mock_client_call(mocker, 'get', response) as m:
        output = client_execute(workdir, [
            'get', 'objective', 'fakekey'
        ])
    assert m.is_called()
    assert datastore.OBJECTIVE['key'] in output
