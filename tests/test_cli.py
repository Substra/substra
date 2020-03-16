# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re
import sys
from unittest import mock
import traceback

import click
from click.testing import CliRunner
import pytest

import substra
from substra.cli.interface import cli, error_printer

from . import datastore


@pytest.fixture
def workdir(tmp_path):
    d = tmp_path / "substra-cli"
    d.mkdir()
    return d


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
    if '--config' not in command:
        cfgpath = directory / 'substra.cfg'
        substra.sdk.config.Manager(str(cfgpath)).add_profile(
            'default', 'username', 'password', url='http://foo')
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

    new_url = 'http://foo'
    new_profile = 'foo'
    execute([
        'config',
        new_url,
        '--profile', new_profile,
        '--config', str(cfgfile),
        '-u', 'foo',
        '-p', 'bar'
    ])
    assert cfgfile.exists()

    # check new profile has been created, check also that default profile
    # has been created
    with cfgfile.open() as fp:
        cfg = json.load(fp)
    expected_profiles = ['default', 'foo']
    assert list(cfg.keys()) == expected_profiles


def mock_client_call(mocker, method_name, response="", side_effect=None):
    return mocker.patch(f'substra.cli.interface.Client.{method_name}',
                        return_value=response, side_effect=side_effect)


def test_command_login(workdir, mocker):
    m = mock_client_call(mocker, 'login')
    client_execute(workdir, ['login'])
    m.assert_called()


@pytest.mark.parametrize('asset_name,key_field', [
    ('objective', 'key'),
    ('dataset', 'key'),
    ('algo', 'key'),
    ('aggregate_algo', 'key'),
    ('composite_algo', 'key'),
    ('testtuple', 'key'),
    ('traintuple', 'key'),
    ('aggregatetuple', 'key'),
    ('composite_traintuple', 'key'),
    ('compute_plan', 'computePlanID'),
])
def test_command_list(asset_name, key_field, workdir, mocker):
    item = getattr(datastore, asset_name.upper())
    method_name = f'list_{asset_name}'
    m = mock_client_call(mocker, method_name, [item])
    output = client_execute(workdir, ['list', asset_name])
    m.assert_called()
    assert item[key_field] in output


def test_command_list_node(workdir, mocker):
    mock_client_call(mocker, 'list_node', datastore.NODES)
    output = client_execute(workdir, ['list', 'node'])
    assert output == ('NODE ID                     \n'
                      'foo                         \n'
                      'bar         (current)       \n')


@pytest.mark.parametrize('asset_name,params', [
    ('dataset', []),
    ('algo', []),
    ('aggregate_algo', []),
    ('composite_algo', []),
    ('traintuple', ['--algo-key', 'foo', '--dataset-key', 'foo',
                    '--data-samples-path']),
    ('traintuple', ['--algo-key', 'foo', '--dataset-key', 'foo',
                    '--in-model-key', 'foo', '--data-samples-path']),
    ('traintuple', ['--algo-key', 'foo', '--dataset-key', 'foo',
                    '--in-model-key', 'foo', '--in-model-key', 'bar', '--data-samples-path']),
    ('testtuple', ['--objective-key', 'foo', '--traintuple-key', 'foo', '--data-samples-path']),
    ('compute_plan', []),
    ('composite_traintuple', ['--algo-key', 'foo', '--dataset-key', 'foo', '--data-samples-path']),
])
def test_command_add(asset_name, params, workdir, mocker):
    method_name = f'add_{asset_name}'

    m = mock_client_call(mocker, method_name, response={})
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    client_execute(workdir, ['add', asset_name] + params + [str(json_file)])
    m.assert_called()

    invalid_json_file = workdir / "invalid_json_file.txt"
    invalid_json_file.write_text("foo")

    res = client_execute(workdir, ['add', asset_name] + params + [str(invalid_json_file)],
                         exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)

    res = client_execute(workdir, ['add', asset_name] + params + ['non_existing_file.txt'],
                         exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)


def test_command_add_objective(workdir, mocker):
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))

    m = mock_client_call(mocker, 'add_objective', response={})
    client_execute(workdir, ['add', 'objective', str(json_file), '--dataset-key', 'foo',
                             '--data-samples-path', str(json_file)])
    m.assert_called()

    m = mock_client_call(mocker, 'add_objective', response={})
    client_execute(workdir, ['add', 'objective', str(json_file)])
    m.assert_called()

    res = client_execute(workdir, ['add', 'objective', 'non_existing_file.txt', '--dataset-key',
                                   'foo', '--data-samples-path', str(json_file)], exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)

    res = client_execute(workdir, ['add', 'objective', str(json_file), '--dataset-key', 'foo',
                                   '--data-samples-path', 'non_existing_file.txt'], exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)

    invalid_json_file = workdir / "invalid_json_file.md"
    invalid_json_file.write_text("test")

    res = client_execute(workdir, ['add', 'objective', str(invalid_json_file), '--dataset-key',
                                   'foo', '--data-samples-path', str(json_file)], exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)

    res = client_execute(workdir, ['add', 'objective', str(json_file), '--dataset-key',
                                   'foo', '--data-samples-path', str(invalid_json_file)],
                         exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)


@pytest.mark.parametrize('params', [
    ([]),
    (['--head-model-key', 'e', '--trunk-model-key', 'e'])
])
def test_command_add_composite_traintuple(mocker, workdir, params):
    m = mock_client_call(mocker, 'add_composite_traintuple', response={})
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    client_execute(workdir, ['add', 'composite_traintuple', '--algo-key', 'foo', '--dataset-key',
                             'foo'] + params + ['--data-samples-path', str(json_file)])
    m.assert_called()


@pytest.mark.parametrize('params,message', [
    (['--head-model-key', 'e'], r'The --trunk-model-key option is required'),
    (['--trunk-model-key', 'e'], r'The --head-model-key option is required')
])
def test_command_add_composite_traintuple_missing_model_key(mocker, workdir, params, message):
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    res = client_execute(workdir, ['add', 'composite_traintuple', '--algo-key', 'foo',
                                   '--dataset-key', 'foo', '--data-samples-path', str(json_file)]
                         + params, exit_code=2)
    assert re.search(message, res)


@pytest.mark.parametrize('params', [
    [],
    ['--in-model-key', 'bar']
])
def test_command_add_aggregatetuple(mocker, workdir, params):
    m = mock_client_call(mocker, 'add_aggregatetuple', response={})
    client_execute(workdir, ['add', 'aggregatetuple', '--algo-key', 'foo',
                             '--in-model-key', 'foo'] + params + ['--worker', 'foo'])
    m.assert_called()


def test_command_add_testtuple_no_data_samples(mocker, workdir):
    m = mock_client_call(mocker, 'add_testtuple', response={})
    client_execute(workdir, ['add', 'testtuple', '--objective-key', 'foo',
                             '--traintuple-key', 'foo'])
    m.assert_called()


def test_command_add_data_sample(workdir, mocker):
    temp_dir = workdir / "test"
    temp_dir.mkdir()

    m = mock_client_call(mocker, 'add_data_samples')
    client_execute(workdir, ['add', 'data_sample', str(temp_dir), '--dataset-key', 'foo',
                             '--test-only'])
    m.assert_called()

    res = client_execute(workdir, ['add', 'data_sample', 'dir', '--dataset-key', 'foo'],
                         exit_code=2)
    assert re.search(r"Directory '.*' does not exist\.", res)


@pytest.mark.parametrize('asset_name, params', [
    ('dataset', []),
    ('algo', []),
    ('traintuple', ['--algo-key', 'foo', '--dataset-key', 'foo',
                    '--data-samples-path']),
    ('testtuple', ['--objective-key', 'foo', '--traintuple-key', 'foo', '--data-samples-path']),
    ('compute_plan', []),
    ('objective', []),
])
def test_command_add_already_exists(workdir, mocker, asset_name, params):
    m = mock_client_call(mocker, f'add_{asset_name}',
                         side_effect=substra.exceptions.AlreadyExists('foo', 409))
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    output = client_execute(workdir, ['add', asset_name] + params + [str(json_file)],
                            exit_code=1)

    assert 'already exists' in output
    m.assert_called()


def test_command_add_data_sample_already_exists(workdir, mocker):
    m = mock_client_call(mocker, 'add_data_samples',
                         side_effect=substra.exceptions.AlreadyExists('foo', 409))
    temp_dir = workdir / "test"
    temp_dir.mkdir()
    output = client_execute(workdir, ['add', 'data_sample', str(temp_dir), '--dataset-key', 'foo'],
                            exit_code=1)
    assert 'already exists' in output
    m.assert_called()


@pytest.mark.parametrize('asset_name,key_field', [
    ('objective', 'key'),
    ('dataset', 'key'),
    ('algo', 'key'),
    ('aggregate_algo', 'key'),
    ('composite_algo', 'key'),
    ('testtuple', 'key'),
    ('traintuple', 'key'),
    ('aggregatetuple', 'key'),
    ('composite_traintuple', 'key'),
    ('compute_plan', 'computePlanID'),
])
def test_command_get(asset_name, key_field, workdir, mocker):
    item = getattr(datastore, asset_name.upper())
    method_name = f'get_{asset_name}'
    m = mock_client_call(mocker, method_name, item)
    output = client_execute(workdir, ['get', asset_name, 'fakekey'])
    m.assert_called()
    assert item[key_field] in output


def test_command_describe(workdir, mocker):
    response = "My description."
    m = mock_client_call(mocker, 'describe_objective', response)
    output = client_execute(workdir, ['describe', 'objective', 'fakekey'])
    m.assert_called()
    assert response in output


def test_command_download(workdir, mocker):
    m = mock_client_call(mocker, 'download_objective')
    client_execute(workdir, ['download', 'objective', 'fakekey'])
    m.assert_called()


def test_command_cancel_compute_plan(workdir, mocker):
    m = mock_client_call(mocker, 'cancel_compute_plan', datastore.COMPUTE_PLAN)
    client_execute(workdir, ['cancel', 'compute_plan', 'fakekey'])
    m.assert_called()


def test_command_leaderboard(workdir, mocker):
    m = mock_client_call(mocker, 'leaderboard', datastore.LEADERBOARD)
    client_execute(workdir, ['leaderboard', 'fakekey'])
    m.assert_called()


def test_command_update_dataset(workdir, mocker):
    m = mock_client_call(mocker, 'update_dataset')
    client_execute(workdir, ['update', 'dataset', 'key1', 'key2'])
    m.assert_called()


def test_command_update_data_sample(workdir, mocker):
    data_samples = {
        'keys': ['key1', 'key2'],
    }

    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps(data_samples))

    m = mock_client_call(mocker, 'link_dataset_with_data_samples')
    client_execute(workdir, ['update', 'data_sample', str(json_file), '--dataset-key', 'foo'])
    m.assert_called()

    invalid_json_file = workdir / "invalid_json_file.json"
    invalid_json_file.write_text('test')

    res = client_execute(workdir, ['update', 'data_sample', str(invalid_json_file), '--dataset-key',
                                   'foo'], exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)

    res = client_execute(workdir, ['update', 'data_sample', 'non_existing_file.txt',
                                   '--dataset-key', 'foo'], exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)


@pytest.mark.parametrize('exception', [
    (substra.exceptions.RequestException("foo", 400)),
    (substra.exceptions.ConnectionError("foo", 400)),
    (substra.exceptions.InvalidResponse(None, 'foo')),
    (substra.exceptions.LoadDataException("foo", 400)),
])
def test_error_printer(mocker, exception):
    @error_printer
    def foo():
        raise exception

    mock_click_context = mock.MagicMock()
    mock_click_context.obj.verbose = False

    mocker.patch('substra.cli.interface.click.get_current_context', return_value=mock_click_context)
    with pytest.raises(click.ClickException, match='foo'):
        foo()
