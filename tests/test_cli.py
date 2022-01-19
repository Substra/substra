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
import traceback
from unittest import mock

import click
import pytest
import yaml
from click.testing import CliRunner

import substra
from substra.cli.interface import cli
from substra.cli.interface import error_printer
from substra.sdk import models

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


@pytest.mark.parametrize(
    "asset_name,model",
    [
        ("metric", models.Metric),
        ("dataset", models.Dataset),
        ("algo", models.Algo),
        ("testtuple", models.Testtuple),
        ("traintuple", models.Traintuple),
        ("aggregatetuple", models.Aggregatetuple),
        ("composite_traintuple", models.CompositeTraintuple),
        ("compute_plan", models.ComputePlan),
    ],
)
@pytest.mark.parametrize("format", ["pretty", "json", "yaml"])
def test_command_list(asset_name, model, format, workdir, mocker):
    item = model(**getattr(datastore, asset_name.upper()))
    method_name = f"list_{asset_name}"
    m = mock_client_call(mocker, method_name, [item])
    output = client_execute(workdir, ["list", asset_name, "-o", format])
    m.assert_called()
    assert item.key in output


def test_command_list_node(workdir, mocker):
    mock_client_call(mocker, "list_node", [models.Node(**node) for node in datastore.NODES])
    output = client_execute(workdir, ["list", "node"])
    assert output == (
        "NODE ID                     \n" "foo                         \n" "bar         (current)       \n"
    )


@pytest.mark.parametrize(
    "asset_name,params",
    [
        ("dataset", []),
        ("algo", []),
        ("traintuple", ["--algo-key", "foo", "--dataset-key", "foo", "--data-samples-path"]),
        ("traintuple", ["--algo-key", "foo", "--dataset-key", "foo", "--in-model-key", "foo", "--data-samples-path"]),
        (
            "traintuple",
            [
                "--algo-key",
                "foo",
                "--dataset-key",
                "foo",
                "--in-model-key",
                "foo",
                "--in-model-key",
                "bar",
                "--data-samples-path",
            ],
        ),
        ("testtuple", ["--metric-key", "foo", "--traintuple-key", "foo", "--data-samples-path"]),
        ("compute_plan", []),
        ("composite_traintuple", ["--algo-key", "foo", "--dataset-key", "foo", "--data-samples-path"]),
    ],
)
def test_command_add(asset_name, params, workdir, mocker):
    method_name = f"add_{asset_name}"

    if asset_name == "compute_plan":
        m = mock_client_call(mocker, method_name, response={"key": "foo"})
    else:
        m = mock_client_call(mocker, method_name, response="foo")
    item = getattr(datastore, asset_name.upper())
    mock_client_call(mocker, f"get_{asset_name}", item)

    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    client_execute(workdir, ["add", asset_name] + params + [str(json_file)])
    m.assert_called()

    invalid_json_file = workdir / "invalid_json_file.txt"
    invalid_json_file.write_text("foo")

    res = client_execute(workdir, ["add", asset_name] + params + [str(invalid_json_file)], exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)

    res = client_execute(workdir, ["add", asset_name] + params + ["non_existing_file.txt"], exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)


def test_command_add_metric(workdir, mocker):
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))

    m = mock_client_call(mocker, "add_metric", response="foo")
    item = getattr(datastore, "METRIC")  # noqa: B009
    m = mock_client_call(mocker, "get_metric", item)

    client_execute(workdir, ["add", "metric", str(json_file)])
    m.assert_called()

    m = mock_client_call(mocker, "add_metric", response={})
    client_execute(workdir, ["add", "metric", str(json_file)])
    m.assert_called()

    res = client_execute(workdir, ["add", "metric", "non_existing_file.txt"], exit_code=2)
    assert re.search(r"File '.*' does not exist\.", res)

    invalid_json_file = workdir / "invalid_json_file.md"
    invalid_json_file.write_text("test")

    res = client_execute(workdir, ["add", "metric", str(invalid_json_file)], exit_code=2)
    assert re.search(r"File '.*' is not a valid JSON file\.", res)


@pytest.mark.parametrize("params", [([]), (["--head-model-key", "e", "--trunk-model-key", "e"])])
def test_command_add_composite_traintuple(mocker, workdir, params):
    m = mock_client_call(mocker, "add_composite_traintuple", response="foo")
    item = getattr(datastore, "composite_traintuple".upper())
    m = mock_client_call(mocker, "get_composite_traintuple", item)
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    client_execute(
        workdir,
        ["add", "composite_traintuple", "--algo-key", "foo", "--dataset-key", "foo"]
        + params
        + ["--data-samples-path", str(json_file)],
    )
    m.assert_called()


@pytest.mark.parametrize(
    "params,message",
    [
        (["--head-model-key", "e"], r"The --trunk-model-key option is required"),
        (["--trunk-model-key", "e"], r"The --head-model-key option is required"),
    ],
)
def test_command_add_composite_traintuple_missing_model_key(mocker, workdir, params, message):
    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps({}))
    res = client_execute(
        workdir,
        [
            "add",
            "composite_traintuple",
            "--algo-key",
            "foo",
            "--dataset-key",
            "foo",
            "--data-samples-path",
            str(json_file),
        ]
        + params,
        exit_code=2,
    )
    assert re.search(message, res)


@pytest.mark.parametrize("params", [[], ["--in-model-key", "bar"]])
def test_command_add_aggregatetuple(mocker, workdir, params):
    m = mock_client_call(mocker, "add_aggregatetuple", response="foo")
    item = getattr(datastore, "aggregatetuple".upper())
    m = mock_client_call(mocker, "get_aggregatetuple", item)
    client_execute(
        workdir, ["add", "aggregatetuple", "--algo-key", "foo", "--in-model-key", "foo"] + params + ["--worker", "foo"]
    )
    m.assert_called()


def test_command_add_testtuple_no_data_samples(mocker, workdir):
    m = mock_client_call(mocker, "add_testtuple", response="foo")
    item = getattr(datastore, "testtuple".upper())
    m = mock_client_call(mocker, "get_testtuple", item)
    client_execute(workdir, ["add", "testtuple", "--metric-key", "foo", "--traintuple-key", "foo"])
    m.assert_called()


def test_command_add_data_sample(workdir, mocker):
    temp_dir = workdir / "test"
    temp_dir.mkdir()

    m = mock_client_call(mocker, "add_data_samples")
    client_execute(workdir, ["add", "data_sample", str(temp_dir), "--dataset-key", "foo", "--test-only"])
    m.assert_called()

    res = client_execute(workdir, ["add", "data_sample", "dir", "--dataset-key", "foo"], exit_code=2)
    assert re.search(r"Directory '.*' does not exist\.", res)


def test_command_add_data_sample_already_exists(workdir, mocker):
    m = mock_client_call(mocker, "add_data_samples", side_effect=substra.exceptions.AlreadyExists("foo", 409))
    temp_dir = workdir / "test"
    temp_dir.mkdir()
    output = client_execute(workdir, ["add", "data_sample", str(temp_dir), "--dataset-key", "foo"], exit_code=1)
    assert "already exist" in output
    m.assert_called()


@pytest.mark.parametrize(
    "asset_name,model",
    [
        ("metric", models.Metric),
        ("dataset", models.Dataset),
        ("algo", models.Algo),
        ("testtuple", models.Testtuple),
        ("traintuple", models.Traintuple),
        ("aggregatetuple", models.Aggregatetuple),
        ("composite_traintuple", models.CompositeTraintuple),
        ("compute_plan", models.ComputePlan),
    ],
)
@pytest.mark.parametrize("format", ["pretty", "json", "yaml"])
def test_command_get(asset_name, model, format, workdir, mocker):
    item = model(**getattr(datastore, asset_name.upper()))
    method_name = f"get_{asset_name}"
    m = mock_client_call(mocker, method_name, item)
    output = client_execute(workdir, ["get", asset_name, "fakekey", "-o", format])
    m.assert_called()
    assert item.key in output
    if format == "json":
        json.loads(output)
    elif format == "yaml":
        yaml.load(output, Loader=yaml.Loader)


def test_command_describe(workdir, mocker):
    response = "My description."
    m = mock_client_call(mocker, "describe_metric", response)
    output = client_execute(workdir, ["describe", "metric", "fakekey"])
    m.assert_called()
    assert response in output


def test_command_download(workdir, mocker):
    m = mock_client_call(mocker, "download_metric")
    client_execute(workdir, ["download", "metric", "fakekey"])
    m.assert_called()


def test_command_download_model(workdir, mocker):
    m = mock_client_call(mocker, "download_model")
    client_execute(workdir, ["download", "model", "fakekey"])
    m.assert_called()

    m = mock_client_call(mocker, "download_model_from_traintuple")
    client_execute(workdir, ["download", "model", "--from-traintuple", "fakekey"])
    m.assert_called()

    m = mock_client_call(mocker, "download_model_from_aggregatetuple")
    client_execute(workdir, ["download", "model", "--from-aggregatetuple", "fakekey"])
    m.assert_called()

    m = mock_client_call(mocker, "download_head_model_from_composite_traintuple")
    client_execute(workdir, ["download", "model", "--from-composite-head", "fakekey"])
    m.assert_called()

    m = mock_client_call(mocker, "download_trunk_model_from_composite_traintuple")
    client_execute(workdir, ["download", "model", "--from-composite-trunk", "fakekey"])
    m.assert_called()


def test_command_logs(workdir, mocker):
    m = mock_client_call(mocker, "get_logs")
    client_execute(workdir, ["logs", "fakekey"])
    m.assert_called()

    m = mock_client_call(mocker, "download_logs")
    client_execute(workdir, ["logs", "fakekey", "--output-dir", "."])
    m.assert_called()


def test_command_cancel_compute_plan(workdir, mocker):
    m = mock_client_call(mocker, "cancel_compute_plan", models.ComputePlan(**datastore.COMPUTE_PLAN))
    client_execute(workdir, ["cancel", "compute_plan", "fakekey"])
    m.assert_called()


def test_command_update_data_sample(workdir, mocker):
    data_samples = {
        "keys": ["key1", "key2"],
    }

    json_file = workdir / "valid_json_file.json"
    json_file.write_text(json.dumps(data_samples))

    m = mock_client_call(mocker, "link_dataset_with_data_samples")
    client_execute(workdir, ["update", "data_sample", str(json_file), "--dataset-key", "foo"])
    m.assert_called()

    invalid_json_file = workdir / "invalid_json_file.json"
    invalid_json_file.write_text("test")

    res = client_execute(
        workdir, ["update", "data_sample", str(invalid_json_file), "--dataset-key", "foo"], exit_code=2
    )
    assert re.search(r"File '.*' is not a valid JSON file\.", res)

    res = client_execute(
        workdir, ["update", "data_sample", "non_existing_file.txt", "--dataset-key", "foo"], exit_code=2
    )
    assert re.search(r"File '.*' does not exist\.", res)


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


def test_command_get_model_None(workdir, mocker):
    item = models.CompositeTraintuple(**datastore.COMPOSITE_TRAINTUPLE_DOING)
    m = mock_client_call(mocker, "get_composite_traintuple", item)
    output = client_execute(workdir, ["get", "composite_traintuple", "fakekey"])
    m.assert_called()
    assert item.key in output


@pytest.mark.parametrize("format", ["pretty", "json", "yaml"])
def test_command_get_testtuple_metric_key_not_None(workdir, mocker, format):
    # test if the metric key is present in `substra get testtuple`
    item = models.Testtuple(**getattr(datastore, "TESTTUPLE"))
    method_name = "get_testtuple"
    m = mock_client_call(mocker, method_name, item)
    output = client_execute(workdir, ["get", "testtuple", "fakekey", "-o", format])
    m.assert_called()
    metric_key = "e526243f-f51a-4737-9fea-a5d55f4205fe"
    perfs = "0.82681566"
    assert metric_key in output
    assert perfs in output
