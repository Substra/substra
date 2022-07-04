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

import functools
import json
import logging
import os

import click
import consolemd

from substra import __version__
from substra.cli import printers
from substra.sdk import assets
from substra.sdk import config as configuration
from substra.sdk import exceptions
from substra.sdk import utils
from substra.sdk.client import DEFAULT_BATCH_SIZE
from substra.sdk.client import Client

DEFAULT_RETRY_TIMEOUT = 300


def get_client(global_conf):
    """Initialize substra client from config file, profile name and tokens file."""
    help_command = "substra config <url> ..."

    try:
        client = Client.from_config_file(
            config_path=global_conf.config,
            profile_name=global_conf.profile,
            tokens_path=global_conf.tokens,
        )

    except FileNotFoundError:
        raise click.ClickException(f"Config file '{global_conf.config}' not found. Please run '{help_command}'.")

    except configuration.ProfileNotFoundError:
        raise click.ClickException(f"Profile '{global_conf.profile}' not found. Please run '{help_command}'.")

    return client


def load_json_from_path(ctx, param, value):
    if not value:
        return value

    with open(value, "r") as fp:
        try:
            json_file = json.load(fp)
        except json.decoder.JSONDecodeError:
            raise click.BadParameter(f"File '{value}' is not a valid JSON file.")
    return json_file


def display(res):
    """Display result."""
    if res is None:
        return
    if isinstance(res, dict) or isinstance(res, list):
        res = json.dumps(res, indent=2)
    print(res)


class GlobalConf:
    def __init__(self):
        self.profile = None
        self.config = None
        self.tokens = None
        self.verbose = None
        self.output_format = None
        self.retry_timeout = DEFAULT_RETRY_TIMEOUT

    def retry(self, func):
        return utils.retry_on_exception(
            exceptions=(exceptions.RequestTimeout),
            timeout=float(self.retry_timeout),
        )(func)


def update_global_conf(ctx, param, value):
    setattr(ctx.obj, param.name, value)


def click_global_conf_profile(f):
    """Add profile option to command."""
    return click.option(
        "--profile",
        expose_value=False,
        callback=update_global_conf,
        default="default",
        help="Profile name to use.",
    )(f)


def click_global_conf_tokens(f):
    """Add tokens option to command."""
    return click.option(
        "--tokens",
        expose_value=False,
        type=click.Path(dir_okay=False, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_TOKENS_PATH),
        help=f"Tokens file path to use (default {configuration.DEFAULT_TOKENS_PATH}).",
    )(f)


def click_global_conf_config(f):
    """Add config option to command."""
    return click.option(
        "--config",
        expose_value=False,
        type=click.Path(exists=True, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_PATH),
        help=f"Config path (default {configuration.DEFAULT_PATH}).",
    )(f)


def click_global_conf_verbose(f):
    """Add verbose option to command."""
    return click.option(
        "--verbose",
        expose_value=False,
        callback=update_global_conf,
        is_flag=True,
        help="Enable verbose mode.",
    )(f)


def set_log_level(ctx, param, value):
    if value:
        logging.basicConfig(level=getattr(logging, value))


def click_global_conf_log_level(f):
    """Add verbose option to command."""
    return click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        callback=set_log_level,
        expose_value=False,
        help="Enable logging and set log level",
    )(f)


def click_global_conf_output_format(f):
    """Add output option to command."""
    return click.option(
        "-o",
        "--output",
        "output_format",
        type=click.Choice(["pretty", "yaml", "json"]),
        expose_value=False,
        default="pretty",
        show_default=True,
        callback=update_global_conf,
        help="Set output format                 \
            - pretty: summarised view           \
            - yaml: full view in YAML format    \
            - json: full view in JSON format    \
            ",
    )(f)


def click_global_conf(f):
    f = click_global_conf_verbose(f)
    f = click_global_conf_tokens(f)
    f = click_global_conf_profile(f)
    f = click_global_conf_config(f)
    f = click_global_conf_log_level(f)
    return f


def click_global_conf_with_output_format(f):
    f = click_global_conf_output_format(f)
    f = click_global_conf(f)
    return f


def click_option_metadata(f):
    """Add metadata option to command."""
    return click.option(
        "--metadata-path",
        "metadata",
        callback=load_json_from_path,
        type=click.Path(exists=True, resolve_path=True, dir_okay=False),
        help="Metadata file path",
    )(f)


def click_option_expand(f):
    """Add expand option to command."""
    return click.option("--expand", is_flag=True, help="Display associated assets details")(f)


def click_global_conf_retry_timeout(f):
    """Add timeout option to command."""
    return click.option(
        "--timeout",
        "timeout",
        type=click.INT,
        expose_value=False,
        default=DEFAULT_RETRY_TIMEOUT,
        show_default=True,
        callback=update_global_conf,
        help="Max number of seconds the operation will be retried for",
    )(f)


def validate_json(ctx, param, value):
    if not value:
        return value

    try:
        data = json.loads(value)
    except ValueError:
        raise click.BadParameter("must be valid JSON")
    return data


def load_data_samples_keys(data_samples, option="--data-samples-path"):
    try:
        return data_samples["keys"]
    except KeyError:
        raise click.BadParameter('File must contain a "keys" attribute.', param_hint=f'"{option}"')


def _format_server_errors(fn, errors):
    action = fn.__name__.replace("_", " ")

    def _format_error_lines(errors_):
        lines_ = []
        for field, field_errors in errors_.items():
            for field_error in field_errors:
                lines_.append(f"{field}: {field_error}")
        return lines_

    lines = []
    if isinstance(errors, dict):
        lines += _format_error_lines(errors)
    elif isinstance(errors, list):
        for error in errors:
            lines += _format_error_lines(error)
    else:
        lines.append(errors)

    pluralized_error = "errors" if len(lines) > 1 else "error"
    return (
        f"Could not {action}, the server returned the following \
        {pluralized_error}:\n- "
        + "\n- ".join(lines)
    )


def error_printer(fn):
    """Command decorator to pretty print a few selected exceptions from sdk."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        if ctx.obj.verbose:
            # disable pretty print of errors if verbose mode is activated
            return fn(*args, **kwargs)

        try:
            return fn(*args, **kwargs)
        except exceptions.BadLoginException:
            raise click.ClickException("Login failed: No active account found with the" " given credentials.")
        except exceptions.InvalidRequest as e:
            try:
                errors = e.errors["message"]
            except KeyError:
                errors = e.errors
            raise click.ClickException(_format_server_errors(fn, errors))
        except exceptions.RequestException as e:
            raise click.ClickException(f"Request failed: {e.__class__.__name__}: {e}")
        except (
            exceptions.ConnectionError,
            exceptions.InvalidResponse,
            exceptions.LoadDataException,
            exceptions.BadConfiguration,
        ) as e:
            raise click.ClickException(str(e))

    return wrapper


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """Substra Command Line Interface.

    For help using this tool, please open an issue on the Github repository:
    https://github.com/SubstraFoundation/substra
    """
    ctx.obj = GlobalConf()


@cli.command("config")
@click.argument("url")
@click.option(
    "--config",
    type=click.Path(),
    default=os.path.expanduser(configuration.DEFAULT_PATH),
    help=f"Config path (default {configuration.DEFAULT_PATH}).",
)
@click.option("--profile", default="default", help="Profile name to add")
@click.option("--insecure", "-k", is_flag=True, help="Do not verify SSL certificates")
def add_profile_to_config(url, config, profile, insecure):
    """Add profile to config file."""
    manager = configuration.ConfigManager(config)
    manager.set_profile(name=profile, url=url, insecure=insecure)
    manager.save()


@cli.command("login")
@click_global_conf
@click.pass_context
@error_printer
@click.option("--username", "-u", envvar="SUBSTRA_USERNAME", prompt=True)
@click.option("--password", "-p", envvar="SUBSTRA_PASSWORD", prompt=True, hide_input=True)
def login(ctx, username, password):
    """Login to the Substra platform."""
    client = get_client(ctx.obj)

    token = client.login(username, password)

    # save token to tokens file
    manager = configuration.TokenManager(ctx.obj.tokens)
    manager.set_profile(ctx.obj.profile, token)
    manager.save()

    display(f"Token: {token}")


@cli.command()
@click.argument("asset-type", type=click.Choice([assets.ALGO, assets.DATASET]))
@click.argument("asset-key")
@click_global_conf
@click.pass_context
@error_printer
def describe(ctx, asset_type, asset_key):
    """Display asset description."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    method = getattr(client, f"describe_{asset_type.lower()}")
    description = method(asset_key)
    renderer = consolemd.Renderer()
    renderer.render(description)


@cli.group()
@click.pass_context
def organization(ctx):
    """Display organization description."""


@organization.command("info")
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def organization_info(ctx):
    """Display organization info."""
    client = get_client(ctx.obj)
    res = client.organization_info()
    printer = printers.OrganizationInfoPrinter()
    printer.print(res)


@cli.command()
@click.argument("asset-type", type=click.Choice([assets.ALGO, assets.DATASET, assets.MODEL]))
@click.argument("key")
@click.option("--folder", type=click.Path(), help="destination folder", default=".")
@click.option(
    "--from-traintuple",
    "model_src",
    help=("(model download only) if this option is set, " "the KEY argument refers to a traintuple key"),
    flag_value="model_from_traintuple",
)
@click.option(
    "--from-aggregatetuple",
    "model_src",
    help=("(model download only) if this option is set, " "the KEY argument refers to an aggregatetuple key"),
    flag_value="model_from_aggregatetuple",
)
@click.option(
    "--from-composite-head",
    "model_src",
    help=("(model download only) if this option is set, " "the KEY argument refers to a composite traintuple key"),
    flag_value="head_model_from_composite_traintuple",
)
@click.option(
    "--from-composite-trunk",
    "model_src",
    help=("(model download only) if this option is set, " "the KEY argument refers to a composite traintuple key"),
    flag_value="trunk_model_from_composite_traintuple",
)
@click_global_conf
@click.pass_context
@error_printer
def download(ctx, asset_type, key, folder, model_src):
    """Download asset implementation.

    \b
    - algo: the algo and its dependencies
    - dataset: the opener script
    - model: the output model
    """
    client = get_client(ctx.obj)

    if asset_type == assets.MODEL:
        method = getattr(client, f"download_{model_src}" if model_src else "download_model")
    else:
        method = getattr(client, f"download_{asset_type.lower()}")

    res = method(key, folder)
    display(res)


@cli.group()
@click.pass_context
def cancel(ctx):
    """Cancel execution of an asset."""
    pass


@cancel.command("compute_plan")
@click.argument("compute_plan_key", type=click.STRING)
@click_global_conf
@click.pass_context
def cancel_compute_plan(ctx, compute_plan_key):
    """Cancel execution of a compute plan."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    client.cancel_compute_plan(compute_plan_key)


@cli.group()
@click.pass_context
def update(ctx):
    """Update asset."""
    pass


@update.command("dataset_data_samples_link")
@click.argument(
    "data_samples",
    type=click.Path(exists=True, dir_okay=False),
    callback=load_json_from_path,
    metavar="DATA_SAMPLES_PATH",
)
@click.option("--dataset-key", required=True)
@click_global_conf
@click.pass_context
@error_printer
def link_dataset_with_data_samples(ctx, data_samples, dataset_key):
    """Link data samples with dataset.

    The data samples path must point to a valid JSON file with the following
    schema:

    \b
    {
        "keys": list[str],
    }

    \b
    Where:
    - keys: list of data sample keys
    """
    client = get_client(ctx.obj)
    res = client.link_dataset_with_data_samples(
        dataset_key, load_data_samples_keys(data_samples, option="DATA_SAMPLES_PATH")
    )
    display(res)


@update.command("compute_plan_tuples")
@click.argument("compute_plan_key", type=click.STRING)
@click.argument(
    "tuples",
    type=click.Path(exists=True, dir_okay=False),
    callback=load_json_from_path,
    metavar="TUPLES_PATH",
)
@click.option("--no-auto-batching", "-n", is_flag=True, help="Disable the auto batching feature")
@click.option(
    "--batch-size",
    "-b",
    type=int,
    help="Batch size for the auto batching",
    default=DEFAULT_BATCH_SIZE,
    show_default=True,
)
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def add_compute_plan_tuples(ctx, compute_plan_key, tuples, no_auto_batching, batch_size):
    """Add tuples to compute plan.

    The tuples path must point to a valid JSON file with the following schema:

    \b
    {
        "traintuples": list[{
            "algo_key": str,
            "data_manager_key": str,
            "train_data_sample_keys": list[str],
            "traintuple_id": str,
            "in_models_ids": list[str],
            "tag": str,
            "metadata": dict,
        }],
        "composite_traintuples": list[{
            "composite_traintuple_id": str,
            "algo_key": str,
            "data_manager_key": str,
            "train_data_sample_keys": list[str],
            "in_head_model_id": str,
            "in_trunk_model_id": str,
            "out_trunk_model_permissions": {
                "authorized_ids": list[str],
            },
            "tag": str,
            "metadata": dict,
        }]
        "aggregatetuples": list[{
            "aggregatetuple_id": str,
            "algo_key": str,
            "worker": str,
            "in_models_ids": list[str],
            "tag": str,
            "metadata": dict,
        }],
        "testtuples": list[{
            "metric_keys": list[str],
            "data_manager_key": str,
            "test_data_sample_keys": list[str],
            "traintuple_id": str,
            "tag": str,
            "metadata": dict,
        }]
    }

    Disable the auto batching to upload all the tuples of the
    compute plan at once.
    If the auto batching is enabled, change the `batch_size` to define the number of
    tuples uploaded in each batch (default 20).
    """
    if no_auto_batching and batch_size:
        raise click.BadOptionUsage(
            "--batch_size",
            "The --batch_size option cannot be used when using " "--no_auto_batching.",
        )
    client = get_client(ctx.obj)
    res = client.add_compute_plan_tuples(compute_plan_key, tuples, not no_auto_batching, batch_size)
    printer = printers.get_asset_printer(assets.COMPUTE_PLAN, ctx.obj.output_format)
    printer.print(res, is_list=False)


@cli.command()
@click.argument("tuple-key", type=click.STRING)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="The directory the logs must be downloaded to. If not set, the logs are outputted to stdout.",
)
@click_global_conf
@click.pass_context
@error_printer
def logs(ctx, tuple_key, output_dir):
    """Display or download the logs of a failed tuple.

    When an output directory is set, the logs are saved in the directory to a file named
    'tuple_logs_{tuple_key}.txt'. Otherwise, the logs are outputted to stdout.

    Logs are only available for tuples that experienced an execution failure.
    Attempting to retrieve logs for tuples in any other states or for non-existing
    tuples will result in an error.
    """
    client = get_client(ctx.obj)

    if output_dir:
        out_file_path = client.download_logs(tuple_key, output_dir)
        display(f"Logs saved to {out_file_path}")
    else:
        logs_content = client.get_logs(tuple_key)
        display(logs_content)


if __name__ == "__main__":
    cli()
