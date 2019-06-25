import json

from click.testing import CliRunner
import pytest

import substra
from substra.cli.interface import cli


def mock_substra():
    pass


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-cli"
    d.mkdir()
    return d


def command_runner(command, exit_code=0):
    runner = CliRunner()
    result = runner.invoke(cli, command)
    print(result.output)
    assert result.exit_code == exit_code
    return result.output


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
