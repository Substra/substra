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
import functools
import os
import logging

import click
import consolemd

from substra import __version__
from substra.cli import printers
from substra.sdk import assets, exceptions, utils
from substra.sdk import config as configuration
from substra.sdk.client import Client, DEFAULT_BATCH_SIZE

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
        raise click.ClickException(
            f"Config file '{global_conf.config}' not found. Please run '{help_command}'.")

    except configuration.ProfileNotFoundError:
        raise click.ClickException(
            f"Profile '{global_conf.profile}' not found. Please run '{help_command}'.")

    return client


def load_json_from_path(ctx, param, value):
    if not value:
        return value

    with open(value, 'r') as fp:
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
        '--profile',
        expose_value=False,
        callback=update_global_conf,
        default='default',
        help='Profile name to use.')(f)


def click_global_conf_tokens(f):
    """Add tokens option to command."""
    return click.option(
        '--tokens',
        expose_value=False,
        type=click.Path(dir_okay=False, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_TOKENS_PATH),
        help=f'Tokens file path to use (default {configuration.DEFAULT_TOKENS_PATH}).')(f)


def click_global_conf_config(f):
    """Add config option to command."""
    return click.option(
        '--config',
        expose_value=False,
        type=click.Path(exists=True, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_PATH),
        help=f'Config path (default {configuration.DEFAULT_PATH}).')(f)


def click_global_conf_verbose(f):
    """Add verbose option to command."""
    return click.option(
        '--verbose',
        expose_value=False,
        callback=update_global_conf,
        is_flag=True,
        help='Enable verbose mode.'
    )(f)


def set_log_level(ctx, param, value):
    if value:
        logging.basicConfig(level=getattr(logging, value))


def click_global_conf_log_level(f):
    """Add verbose option to command."""
    return click.option(
        '--log-level',
        type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
        callback=set_log_level,
        expose_value=False,
        help='Enable logging and set log level'
    )(f)


def click_global_conf_output_format(f):
    """Add output option to command."""
    return click.option(
        '-o', '--output', 'output_format',
        type=click.Choice(['pretty', 'yaml', 'json']),
        expose_value=False,
        default='pretty',
        show_default=True,
        callback=update_global_conf,
        help='Set output format'
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
        '--metadata-path',
        'metadata',
        callback=load_json_from_path,
        type=click.Path(exists=True, resolve_path=True, dir_okay=False),
        help='Metadata file path')(f)


def click_option_expand(f):
    """Add expand option to command."""
    return click.option(
        '--expand',
        is_flag=True,
        help="Display associated assets details"
    )(f)


def click_global_conf_retry_timeout(f):
    """Add timeout option to command."""
    return click.option(
        '--timeout', 'timeout',
        type=click.INT,
        expose_value=False,
        default=DEFAULT_RETRY_TIMEOUT,
        show_default=True,
        callback=update_global_conf,
        help='Max number of seconds the operation will be retried for'
    )(f)


def validate_json(ctx, param, value):
    if not value:
        return value

    try:
        data = json.loads(value)
    except ValueError:
        raise click.BadParameter('must be valid JSON')
    return data


def load_data_samples_keys(data_samples, option="--data-samples-path"):
    try:
        return data_samples['keys']
    except KeyError:
        raise click.BadParameter('File must contain a "keys" attribute.', param_hint=f'"{option}"')


def _format_server_errors(fn, errors):
    action = fn.__name__.replace('_', ' ')

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

    pluralized_error = 'errors' if len(lines) > 1 else 'error'
    return f"Could not {action}, the server returned the following \
        {pluralized_error}:\n- " + '\n- '.join(lines)


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
            raise click.ClickException('Login failed: No active account found with the'
                                       ' given credentials.')
        except exceptions.InvalidRequest as e:
            try:
                errors = e.errors['message']
            except KeyError:
                errors = e.errors
            raise click.ClickException(_format_server_errors(fn, errors))
        except exceptions.RequestException as e:
            raise click.ClickException(f"Request failed: {e.__class__.__name__}: {e}")
        except (exceptions.ConnectionError,
                exceptions.InvalidResponse,
                exceptions.LoadDataException,
                exceptions.BadConfiguration) as e:
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


@cli.command('config')
@click.argument('url')
@click.option('--config', type=click.Path(),
              default=os.path.expanduser(configuration.DEFAULT_PATH),
              help=f'Config path (default {configuration.DEFAULT_PATH}).')
@click.option('--profile', default='default',
              help='Profile name to add')
@click.option('--insecure', '-k', is_flag=True,
              help='Do not verify SSL certificates')
def add_profile_to_config(url, config, profile, insecure):
    """Add profile to config file."""
    manager = configuration.ConfigManager(config)
    manager.set_profile(name=profile, url=url, insecure=insecure)
    manager.save()


@cli.command('login')
@click_global_conf
@click.pass_context
@error_printer
@click.option('--username', '-u', envvar='SUBSTRA_USERNAME', prompt=True)
@click.option('--password', '-p', envvar='SUBSTRA_PASSWORD', prompt=True, hide_input=True)
def login(ctx, username, password):
    """Login to the Substra platform."""
    client = get_client(ctx.obj)

    token = client.login(username, password)

    # save token to tokens file
    manager = configuration.TokenManager(ctx.obj.tokens)
    manager.set_profile(ctx.obj.profile, token)
    manager.save()

    display(f"Token: {token}")


@cli.group()
@click.pass_context
def add(ctx):
    """Add new asset to Substra platform."""
    pass


@add.command('data_sample')
@click.argument('path', type=click.Path(exists=True, file_okay=False))
@click.option('--dataset-key', required=True)
@click.option('--local/--remote', 'local', is_flag=True, default=True,
              help='Data sample(s) location.')
@click.option('--multiple', is_flag=True, default=False,
              help='Add multiple data samples at once.')
@click.option('--test-only', is_flag=True, default=False,
              help='Data sample(s) used as test data only.')
@click_global_conf
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_data_sample(ctx, path, dataset_key, local, multiple, test_only):
    """Add data sample(s).


    The path is either a directory representing a data sample or a parent
    directory containing data samples directories (if --multiple option is
    set).
    """
    client = get_client(ctx.obj)
    if multiple and local:
        subdirs = next(os.walk(path))[1]
        paths = [os.path.join(path, s) for s in subdirs]
        if not paths:
            raise click.UsageError(f'No data sample directory in {path}')

    else:
        paths = [path]

    data = {
        'paths': paths,
        'data_manager_keys': [dataset_key],
        'multiple': multiple,
    }
    if test_only:
        data['test_only'] = True
    key = client.add_data_samples(data, local=local)
    display(key)


@add.command('dataset')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click.option('--objective-key')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_dataset(ctx, data, objective_key):
    """Add dataset.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "name": str,
        "description": path,
        "type": str,
        "data_opener": path,
        "permissions": {
            "public": bool,
            "authorized_ids": list[str],
        },
        "metadata": dict
    }

    \b
    Where:
    - name: name of the dataset
    - description: path to a markdown file describing the dataset
    - type: short description of the type of data that will be attached to this
      dataset (common values are 'Images', 'Tabular', 'Time series',
      'Spatial time series' and 'Hierarchical images')
    - data_opener: path to the opener python script
    - permissions: define asset access permissions
    """
    client = get_client(ctx.obj)
    if objective_key:  # overwrite data values if set
        data['objective_key'] = objective_key

    key = client.add_dataset(data)
    res = ctx.obj.retry(client.get_dataset)(key)
    printer = printers.get_asset_printer(assets.DATASET, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('objective')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click.option('--dataset-key')
@click.option('--data-samples-path', 'data_samples',
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path, help='Test data samples.')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_objective(ctx, data, dataset_key, data_samples):
    """Add objective.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "name": str,
        "description": path,
        "metrics_name": str,
        "metrics": path,
        "permissions": {
            "public": bool,
            "authorized_ids": list[str],
        },
        "metadata": dict
    }

    \b
    Where:
    - name: name of the objective
    - description: path to a markdown file describing the objective
    - metrics_name: name of the metrics
    - metrics: path to tar.gz or zip archive containing the metrics python
      script and its Dockerfile
    - permissions: define asset access permissions

    The option --data-samples-path must point to a valid JSON file with the
    following schema:

    \b
    {
        "keys": list[str],
    }

    \b
    Where:
    - keys: list of test only data sample keys
    """
    client = get_client(ctx.obj)

    if dataset_key:
        data['test_data_manager_key'] = dataset_key

    if data_samples:
        data['test_data_sample_keys'] = load_data_samples_keys(data_samples)

    key = client.add_objective(data)
    res = ctx.obj.retry(client.get_objective)(key)
    printer = printers.get_asset_printer(assets.OBJECTIVE, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_algo(ctx, data):
    """Add algo.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "name": str,
        "description": path,
        "file": path,
        "permissions": {
            "public": bool,
            "authorized_ids": list[str],
        },
        "metadata": dict
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """

    client = get_client(ctx.obj)
    key = client.add_algo(data)
    res = ctx.obj.retry(client.get_algo)(key)
    printer = printers.get_asset_printer(assets.ALGO, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('compute_plan')
@click.argument('data', type=click.Path(exists=True, dir_okay=False),
                callback=load_json_from_path, metavar="PATH")
@click.option('--no-auto-batching', '-n', is_flag=True,
              help='Disable the auto batching feature')
@click.option('--batch-size', '-b', type=int,
              help='Batch size for the auto batching',
              default=DEFAULT_BATCH_SIZE, show_default=True)
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def add_compute_plan(ctx, data, no_auto_batching, batch_size):
    """Add compute plan.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "traintuples": list[{
            "algo_key": str,
            "data_manager_key": str,
            "train_data_sample_keys": list[str],
            "traintuple_id": str,
            "in_models_ids": list[str],
            "tag": str,
            "metadata": dict
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
            "metadata": dict
        }]
        "aggregatetuples": list[{
            "aggregatetuple_id": str,
            "algo_key": str,
            "worker": str,
            "in_models_ids": list[str],
            "tag": str,
            "metadata": dict
        }],
        "testtuples": list[{
            "objective_key": str,
            "data_manager_key": str,
            "test_data_sample_keys": list[str],
            "traintuple_id": str,
            "tag": str,
            "metadata": dict
        }],
        "clean_models": bool,
        "tag": str,
        "metadata": dict
    }

    Disable the auto batching to upload all the tuples of the
    compute plan at once.
    If the auto batching is enabled, change the `batch_size` to define the number of
    tuples uploaded in each batch (default 20).
    """
    if no_auto_batching and batch_size:
        raise click.BadOptionUsage('--batch_size',
                                   "The --batch_size option cannot be used when using "
                                   "--no_auto_batching.")
    client = get_client(ctx.obj)
    res = client.add_compute_plan(data, auto_batching=not no_auto_batching, batch_size=batch_size)
    printer = printers.get_asset_printer(assets.COMPUTE_PLAN, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('aggregate_algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_aggregate_algo(ctx, data):
    """Add aggregate algo.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "name": str,
        "description": path,
        "file": path,
        "permissions": {
            "public": bool,
            "authorized_ids": list[str],
        },
        "metadata": dict
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """

    client = get_client(ctx.obj)
    key = client.add_aggregate_algo(data)
    res = ctx.obj.retry(client.get_aggregate_algo)(key)
    printer = printers.get_asset_printer(assets.AGGREGATE_ALGO, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('composite_algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click.pass_context
@error_printer
def add_composite_algo(ctx, data):
    """Add composite algo.

    The path must point to a valid JSON file with the following schema:

    \b
    {
        "name": str,
        "description": path,
        "file": path,
        "permissions": {
            "public": bool,
            "authorized_ids": list[str],
        },
        "metadata": dict
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """

    client = get_client(ctx.obj)
    key = client.add_composite_algo(data)
    res = ctx.obj.retry(client.get_composite_algo)(key)
    printer = printers.get_asset_printer(assets.COMPOSITE_ALGO, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('traintuple')
@click.option('--algo-key', required=True)
@click.option('--dataset-key', required=True)
@click.option('--data-samples-path', 'data_samples', required=True,
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path)
@click.option('--in-model-key', 'in_models_keys', type=click.STRING, multiple=True,
              help='In model traintuple key.')
@click.option('--tag')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click_option_metadata
@click.pass_context
@error_printer
def add_traintuple(ctx, algo_key, dataset_key, data_samples, in_models_keys, tag, metadata):
    """Add traintuple.

    The option --data-samples-path must point to a valid JSON file with the
    following schema:

    \b
    {
        "keys": list[str],
    }

    \b
    Where:
    - keys: list of data sample keys
    """
    client = get_client(ctx.obj)
    data = {
        'algo_key': algo_key,
        'data_manager_key': dataset_key,
    }

    if data_samples:
        data['train_data_sample_keys'] = load_data_samples_keys(data_samples)

    if tag:
        data['tag'] = tag

    if metadata:
        data['metadata'] = metadata

    if in_models_keys:
        data['in_models_keys'] = in_models_keys
    key = client.add_traintuple(data)
    res = ctx.obj.retry(client.get_traintuple)(key)
    printer = printers.get_asset_printer(assets.TRAINTUPLE, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('aggregatetuple')
@click.option('--algo-key', required=True, help="Aggregate algo key.")
@click.option('--in-model-key', 'in_models_keys', type=click.STRING, multiple=True,
              help='In model traintuple key.')
@click.option('--worker', required=True, help='Node ID for worker execution.')
@click.option('--rank', type=click.INT)
@click.option('--tag')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click_option_metadata
@click.pass_context
@error_printer
def add_aggregatetuple(ctx, algo_key, in_models_keys, worker, rank, tag, metadata):
    """Add aggregatetuple."""
    client = get_client(ctx.obj)
    data = {
        'algo_key': algo_key,
        'worker': worker,
    }

    if in_models_keys:
        data['in_models_keys'] = in_models_keys

    if rank is not None:
        data['rank'] = rank

    if tag:
        data['tag'] = tag

    if metadata:
        data['metadata'] = metadata
    key = client.add_aggregatetuple(data)
    res = ctx.obj.retry(client.get_aggregatetuple)(key)
    printer = printers.get_asset_printer(assets.AGGREGATETUPLE, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('composite_traintuple')
@click.option('--algo-key', required=True)
@click.option('--dataset-key', required=True)
@click.option('--data-samples-path', 'data_samples', required=True,
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path)
@click.option('--head-model-key',
              help='Must be used with --trunk-model-key option.')
@click.option('--trunk-model-key',
              help='Must be used with --head-model-key option.')
@click.option('--out-trunk-model-permissions-path', 'out_trunk_model_permissions',
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path,
              help='Load a permissions file.')
@click.option('--tag')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click_option_metadata
@click.pass_context
@error_printer
def add_composite_traintuple(ctx, algo_key, dataset_key, data_samples, head_model_key,
                             trunk_model_key, out_trunk_model_permissions, tag, metadata):
    """Add composite traintuple.

    The option --data-samples-path must point to a valid JSON file with the
    following schema:

    \b
    {
        "keys": list[str],
    }

    \b
    Where:
    - keys: list of data sample keys

    The option --out-trunk-model-permissions-path must point to a valid JSON file with the
    following schema:

    \b
    {
        "authorized_ids": list[str],
    }
    """

    if head_model_key and not trunk_model_key:
        raise click.BadOptionUsage('--trunk-model-key',
                                   "The --trunk-model-key option is required when using "
                                   "--head-model-key.")
    if trunk_model_key and not head_model_key:
        raise click.BadOptionUsage('--head-model-key',
                                   "The --head-model-key option is required when using "
                                   "--trunk-model-key.")

    client = get_client(ctx.obj)
    data = {
        'algo_key': algo_key,
        'data_manager_key': dataset_key,
        'in_head_model_key': head_model_key,
        'in_trunk_model_key': trunk_model_key,
    }

    if data_samples:
        data['train_data_sample_keys'] = load_data_samples_keys(data_samples)

    if out_trunk_model_permissions:
        data['out_trunk_model_permissions'] = out_trunk_model_permissions

    if tag:
        data['tag'] = tag

    if metadata:
        data['metadata'] = metadata
    key = client.add_composite_traintuple(data)
    res = ctx.obj.retry(client.get_composite_traintuple)(key)
    printer = printers.get_asset_printer(assets.COMPOSITE_TRAINTUPLE, ctx.obj.output_format)
    printer.print(res, is_list=False)


@add.command('testtuple')
@click.option('--objective-key', required=True)
@click.option('--dataset-key')
@click.option('--traintuple-key', required=True)
@click.option('--data-samples-path', 'data_samples',
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path)
@click.option('--tag')
@click_global_conf_with_output_format
@click_global_conf_retry_timeout
@click_option_metadata
@click.pass_context
@error_printer
def add_testtuple(ctx, objective_key, dataset_key, traintuple_key, data_samples, tag, metadata):
    """Add testtuple.

    The option --data-samples-path must point to a valid JSON file with the
    following schema:

    \b
    {
        "keys": list[str],
    }

    \b
    Where:
    - keys: list of data sample keys
    """
    client = get_client(ctx.obj)
    data = {
        'objective_key': objective_key,
        'data_manager_key': dataset_key,
        'traintuple_key': traintuple_key,
    }

    if data_samples:
        data['test_data_sample_keys'] = load_data_samples_keys(data_samples)

    if tag:
        data['tag'] = tag

    if metadata:
        data['metadata'] = metadata
    key = client.add_testtuple(data)
    res = ctx.obj.retry(client.get_testtuple)(key)
    printer = printers.get_asset_printer(assets.TESTTUPLE, ctx.obj.output_format)
    printer.print(res, is_list=False)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPUTE_PLAN,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
    assets.COMPOSITE_TRAINTUPLE,
    assets.AGGREGATETUPLE,
]))
@click.argument('asset-key')
@click_option_expand
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def get(ctx, expand, asset_name, asset_key):
    """Get asset definition."""
    expand_valid_assets = (assets.DATASET, assets.TRAINTUPLE, assets.OBJECTIVE, assets.TESTTUPLE,
                           assets.COMPOSITE_TRAINTUPLE, assets.AGGREGATETUPLE, assets.COMPUTE_PLAN)
    if expand and asset_name not in expand_valid_assets:  # fail fast
        raise click.UsageError(
            f'--expand option is available with assets {expand_valid_assets}')

    client = get_client(ctx.obj)
    # method must exist in sdk
    method = getattr(client, f'get_{asset_name.lower()}')
    res = method(asset_key)
    printer = printers.get_asset_printer(asset_name, ctx.obj.output_format)
    printer.print(res, profile=ctx.obj.profile, expand=expand)


@cli.command('list')
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPUTE_PLAN,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATA_SAMPLE,
    assets.DATASET,
    assets.OBJECTIVE,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
    assets.COMPOSITE_TRAINTUPLE,
    assets.AGGREGATETUPLE,
    assets.NODE,
]))
@click.option('-f', '--filter', 'filters',
              help='Only display assets that exactly match this filter. Valid syntax is: '
                   '<asset>:<property>:<value>',
              multiple=True)
@click.option('--and', 'filters_logical_clause',
              help='Combine filters using logical ANDs',
              flag_value='and',
              default=True)
@click.option('--or', 'filters_logical_clause',
              help='Combine filters using logical ORs',
              flag_value='or')
@click.option('--advanced-filters',
              callback=validate_json,
              help='Filter results using a complex search (must be a JSON array of valid filters). '
                   'Incompatible with the --filter option')
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def list_(ctx, asset_name, filters, filters_logical_clause, advanced_filters):
    """List assets."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    method = getattr(client, f'list_{asset_name.lower()}')
    # handle filters
    if advanced_filters and filters:
        raise click.UsageError('The --filter and --advanced-filters options are mutually exclusive')
    elif filters:
        filters = list(filters)
        if filters_logical_clause == 'or':
            # insert 'OR' between each filter
            n = len(filters)
            for i in range(n - 1):
                filters.insert(i + 1, 'OR')
    elif advanced_filters:
        filters = advanced_filters
    res = method(filters)
    printer = printers.get_asset_printer(asset_name, ctx.obj.output_format)
    dict_res = [result.dict(exclude_none=False, by_alias=True) for result in res]
    printer.print(dict_res, is_list=True)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
]))
@click.argument('asset-key')
@click_global_conf
@click.pass_context
@error_printer
def describe(ctx, asset_name, asset_key):
    """Display asset description."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    method = getattr(client, f'describe_{asset_name.lower()}')
    description = method(asset_key)
    renderer = consolemd.Renderer()
    renderer.render(description)


@cli.group()
@click.pass_context
def node(ctx):
    """Display node description."""


@node.command('info')
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def node_info(ctx):
    """Display node info."""
    client = get_client(ctx.obj)
    res = client.node_info()
    printer = printers.NodeInfoPrinter()
    printer.print(res)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
    assets.MODEL
]))
@click.argument('key')
@click.option('--folder', type=click.Path(), help='destination folder',
              default='.')
@click.option('--from-traintuple', 'model_src',
              help=(
                  '(model download only) if this option is set, '
                  'the KEY argument refers to a traintuple key'
              ),
              flag_value='model_from_traintuple')
@click.option('--from-aggregatetuple', 'model_src',
              help=(
                  '(model download only) if this option is set, '
                  'the KEY argument refers to an aggregatetuple key'
              ),
              flag_value='model_from_aggregatetuple')
@click.option('--from-composite-head', 'model_src',
              help=(
                  '(model download only) if this option is set, '
                  'the KEY argument refers to a composite traintuple key'
              ),
              flag_value='head_model_from_composite_traintuple')
@click.option('--from-composite-trunk', 'model_src',
              help=(
                  '(model download only) if this option is set, '
                  'the KEY argument refers to a composite traintuple key'
              ),
              flag_value='trunk_model_from_composite_traintuple')
@click_global_conf
@click.pass_context
@error_printer
def download(ctx, asset_name, key, folder, model_src):
    """Download asset implementation.

    \b
    - algo: the algo and its dependencies
    - dataset: the opener script
    - objective: the metrics and its dependencies
    - model: the output model
    """
    client = get_client(ctx.obj)

    if asset_name == assets.MODEL:
        method = getattr(client, f'download_{model_src}' if model_src else 'download_model')
    else:
        method = getattr(client, f'download_{asset_name.lower()}')

    res = method(key, folder)
    display(res)


@cli.command()
@click.argument('objective_key')
@click_option_expand
@click.option('--sort',
              type=click.Choice(['asc', 'desc']),
              default='desc',
              show_default=True,
              help='Sort models by highest to lowest perf or vice versa')
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def leaderboard(ctx, expand, objective_key, sort):
    """Display objective leaderboard"""
    client = get_client(ctx.obj)
    board = client.leaderboard(objective_key, sort=sort)
    printer = printers.get_leaderboard_printer(ctx.obj.output_format)
    printer.print(board, expand=expand)


@cli.group()
@click.pass_context
def cancel(ctx):
    """Cancel execution of an asset."""
    pass


@cancel.command('compute_plan')
@click.argument('compute_plan_key', type=click.STRING)
@click_global_conf_with_output_format
@click.pass_context
def cancel_compute_plan(ctx, compute_plan_key):
    """Cancel execution of a compute plan."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    res = client.cancel_compute_plan(compute_plan_key)
    printer = printers.get_asset_printer(assets.COMPUTE_PLAN, ctx.obj.output_format)
    printer.print(res, profile=ctx.obj.profile)


@cli.group()
@click.pass_context
def update(ctx):
    """Update asset."""
    pass


@update.command('data_sample')
@click.argument('data_samples', type=click.Path(exists=True, dir_okay=False),
                callback=load_json_from_path, metavar="DATA_SAMPLES_PATH")
@click.option('--dataset-key', required=True)
@click_global_conf
@click.pass_context
@error_printer
def update_data_sample(ctx, data_samples, dataset_key):
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
        dataset_key, load_data_samples_keys(data_samples, option="DATA_SAMPLES_PATH"))
    display(res)


@update.command('dataset')
@click.argument('dataset-key')
@click.argument('objective-key')
@click_global_conf
@click.pass_context
@error_printer
def update_dataset(ctx, dataset_key, objective_key):
    """Link dataset with objective."""
    client = get_client(ctx.obj)
    res = client.link_dataset_with_objective(dataset_key, objective_key)
    display(res)


@update.command('compute_plan')
@click.argument('compute_plan_key', type=click.STRING)
@click.argument('tuples', type=click.Path(exists=True, dir_okay=False),
                callback=load_json_from_path, metavar="TUPLES_PATH")
@click.option('--no-auto-batching', '-n', is_flag=True,
              help='Disable the auto batching feature')
@click.option('--batch-size', '-b', type=int,
              help='Batch size for the auto batching',
              default=DEFAULT_BATCH_SIZE, show_default=True)
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def update_compute_plan(ctx, compute_plan_key, tuples, no_auto_batching, batch_size):
    """Update compute plan.

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
            "objective_key": str,
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
        raise click.BadOptionUsage('--batch_size',
                                   "The --batch_size option cannot be used when using "
                                   "--no_auto_batching.")
    client = get_client(ctx.obj)
    res = client.update_compute_plan(compute_plan_key, tuples, not no_auto_batching, batch_size)
    printer = printers.get_asset_printer(assets.COMPUTE_PLAN, ctx.obj.output_format)
    printer.print(res, is_list=False)


if __name__ == '__main__':
    cli()
