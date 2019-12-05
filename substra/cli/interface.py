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

import click
import consolemd

from substra import __version__, runner
from substra.cli import printers
from substra.sdk import assets, exceptions
from substra.sdk import config as configuration
from substra.sdk.client import Client
from substra.sdk import user as usr


def get_client(config_path, profile_name, user_path):
    """Initialize substra client from config file, profile name and user file."""
    help_command = "substra config <url> ..."

    try:
        client = Client(config_path, profile_name, user_path)

    except FileNotFoundError:
        raise click.ClickException(
            f"Config file '{config_path}' not found. Please run '{help_command}'.")

    except configuration.ProfileNotFoundError:
        raise click.ClickException(
            f"Profile '{profile_name}' not found. Please run '{help_command}'.")

    return client


def load_json_from_path(ctx, param, value):
    if not value:
        return value

    with open(value, 'r') as fp:
        try:
            json_file = json.load(fp)
        except json.decoder.JSONDecodeError:
            raise click.BadParameter(f'File "{value}" is not a valid JSON file.')
    return json_file


def dict_append_to_optional_field(data, key, value):
    """Append value to a list that may be null."""
    if key in data:
        data[key].append(value)
    else:
        data[key] = [value]


def display(res):
    """Display result."""
    if res is None:
        return
    if isinstance(res, dict) or isinstance(res, list):
        res = json.dumps(res, indent=2)
    print(res)


# TODO profile, config, json and verbose options should be handled in a single
#      decorator to populate a GlobalOption object stored in the context


def click_option_profile(f):
    """Add profile option to command."""
    return click.option(
        '--profile',
        default='default',
        help='Profile name to use.')(f)


def click_option_user(f):
    """Add user option to command."""
    return click.option(
        '--user',
        type=click.Path(dir_okay=False, resolve_path=True),
        default=usr.DEFAULT_PATH,
        help='User file path to use (default ~/.substra-user).')(f)


def click_option_config(f):
    """Add config option to command."""
    return click.option(
        '--config',
        type=click.Path(exists=True, resolve_path=True),
        default=os.path.expanduser('~/.substra'),
        help='Config path (default ~/.substra).')(f)


def click_option_expand(f):
    """Add expand option to command."""
    return click.option(
        '--expand',
        is_flag=True,
        help="Display associated assets details"
    )(f)


def click_option_output_format(f):
    """Add json option to command."""
    flags = [
        click.option(
            '--pretty', 'output_format',
            flag_value='pretty',
            default=True,
            show_default=True,
            help='Pretty print output'
        ),
        click.option(
            '--json', 'output_format',
            flag_value='json',
            help='Display output as json.'
        ),
        click.option(
            '--yaml', 'output_format',
            flag_value='yaml',
            help='Display output as yaml.'
        )
    ]
    for flag in flags:
        f = flag(f)
    return f


def click_option_verbose(f):
    """Add verbose option to command."""
    return click.option(
        '--verbose',
        is_flag=True,
        help='Enable verbose mode.'
    )(f)


def validate_json(ctx, param, value):
    if not value:
        return value

    try:
        data = json.loads(value)
    except ValueError:
        raise click.BadParameter('must be valid JSON')
    return data


def error_printer(fn):
    """Command decorator to pretty print a few selected exceptions from sdk."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        if ctx.params.get('verbose', False):
            # disable pretty print of errors if verbose mode is activated
            return fn(*args, **kwargs)

        try:
            return fn(*args, **kwargs)
        except exceptions.BadLoginException:
            raise click.ClickException('Login failed: No active account found with the'
                                       ' given credentials.')
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
    https://github.com/SubstraFoundation/substra-cli
    """
    pass


@cli.command('config')
@click.argument('url')
@click.option('--config', type=click.Path(),
              default=configuration.DEFAULT_PATH,
              help='Config path (default ~/.substra).')
@click.option('--profile', default='default',
              help='Profile name to add')
@click.option('--insecure', '-k', is_flag=True,
              help='Do not verify SSL certificates')
@click.option('--version', '-v', default=configuration.DEFAULT_VERSION)
@click.option('--username', '-u', required=True)
@click.option('--password', '-p', required=True)
def add_profile_to_config(url, config, profile, insecure, version, username, password):
    """Add profile to config file."""
    configuration.Manager(config).add_profile(
        profile,
        username,
        password,
        url,
        version=version,
        insecure=insecure,
    )


@cli.command('login')
@click_option_config
@click_option_profile
@click_option_user
@error_printer
def login(config, profile, user):
    """Login to the Substra platform."""
    usr.Manager(user).clear_user()
    client = get_client(config, profile, user)

    token = client.login()
    # create temporary user data
    usr.Manager(user).add_user(token)


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
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_data_sample(ctx, path, dataset_key, local, multiple, test_only,
                    config, profile, user, verbose):
    """Add data sample(s).


    The path is either a directory representing a data sample or a parent
    directory containing data samples directories (if --multiple option is
    set).
    """
    client = get_client(config, profile, user)
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
    res = client.add_data_samples(data, local=local)
    display(res)


@add.command('dataset')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click.option('--objective-key')
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_dataset(ctx, data, objective_key, output_format, config, profile, user, verbose):
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
    client = get_client(config, profile, user)
    dict_append_to_optional_field(data, 'objective_keys', objective_key)
    res = client.add_dataset(data)
    printer = printers.get_asset_printer(assets.DATASET, output_format)
    printer.print(res, is_list=False)


@add.command('objective')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click.option('--dataset-key')
@click.option('--data-samples-path', 'data_samples',
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path, help='Test data samples.')
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_objective(ctx, data, dataset_key, data_samples, output_format, config,
                  profile, user, verbose):
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
    client = get_client(config, profile, user)

    if dataset_key:
        data['test_data_manager_key'] = dataset_key

    if data_samples:
        data['test_data_sample_keys'] = data_samples['keys']

    res = client.add_objective(data)
    printer = printers.get_asset_printer(assets.OBJECTIVE, output_format)
    printer.print(res, is_list=False)


@add.command('algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_algo(ctx, data, output_format, config, profile, user, verbose):
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
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """
    client = get_client(config, profile, user)
    res = client.add_algo(data)
    printer = printers.get_asset_printer(assets.ALGO, output_format)
    printer.print(res, is_list=False)


@add.command('compute_plan')
@click.argument('tuples', type=click.Path(exists=True, dir_okay=False),
                callback=load_json_from_path, metavar="TUPLES_PATH")
@click.option('--objective-key', required=True)
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_compute_plan(ctx, tuples, objective_key, output_format,
                     config, profile, user, verbose):
    """Add compute plan.

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
        }],
        "composite_traintuples": list[{
            "algo_key": str,
            "data_manager_key": str,
            "train_data_sample_keys": list[str],
            "in_head_model_id": str,
            "in_trunk_model_id": str,
            "out_trunk_model_permissions": {
                "authorized_ids": list[str],
            },
            "tag": str,
        }]
        "aggregatetuples": list[{
            "algo_key": str,
            "worker": str,
            "in_models_ids": list[str],
            "tag": str,
        }],
        "testtuples": list[{
            "data_manager_key": str,
            "test_data_sample_keys": list[str],
            "testtuple_id": str,
            "traintuple_id": str,
            "tag": str,
        }]
    }

    """
    client = get_client(config, profile, user)
    data = {
        "objective_key": objective_key
    }
    data.update(tuples)
    res = client.add_compute_plan(data)
    printer = printers.get_asset_printer(assets.COMPUTE_PLAN, output_format)
    printer.print(res, is_list=False)


@add.command('aggregate_algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_aggregate_algo(ctx, data, output_format, config, profile, user, verbose):
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
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """
    client = get_client(config, profile, user)
    res = client.add_aggregate_algo(data)
    printer = printers.get_asset_printer(assets.AGGREGATE_ALGO, output_format)
    printer.print(res, is_list=False)


@add.command('composite_algo')
@click.argument('data', type=click.Path(exists=True, dir_okay=False), callback=load_json_from_path,
                metavar="PATH")
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_composite_algo(ctx, data, output_format, config, profile, user, verbose):
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
    }

    \b
    Where:
    - name: name of the algorithm
    - description: path to a markdown file describing the algo
    - file: path to tar.gz or zip archive containing the algorithm python
      script and its Dockerfile
    - permissions: define asset access permissions
    """
    client = get_client(config, profile, user)
    res = client.add_composite_algo(data)
    printer = printers.get_asset_printer(assets.COMPOSITE_ALGO, output_format)
    printer.print(res, is_list=False)


@add.command('traintuple')
@click.option('--objective-key', required=True)
@click.option('--algo-key', required=True)
@click.option('--dataset-key', required=True)
@click.option('--data-samples-path', 'data_samples', required=True,
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path)
@click.option('--in-model-key', 'in_models_keys', type=click.STRING, multiple=True,
              help='In model traintuple key.')
@click.option('--tag')
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_traintuple(ctx, objective_key, algo_key, dataset_key, data_samples, in_models_keys,
                   tag, output_format, config, profile,
                   user, verbose):
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
    client = get_client(config, profile, user)
    data = {
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': dataset_key,
    }

    if data_samples:
        data['train_data_sample_keys'] = data_samples['keys']

    if tag:
        data['tag'] = tag

    if in_models_keys:
        data['in_models_keys'] = in_models_keys
    res = client.add_traintuple(data)
    printer = printers.get_asset_printer(assets.TRAINTUPLE, output_format)
    printer.print(res, is_list=False)


@add.command('aggregatetuple')
@click.option('--objective-key', required=True)
@click.option('--algo-key', required=True)
@click.option('--in-model-key', 'in_models_keys', type=click.STRING, multiple=True,
              help='In model traintuple key.')
@click.option('--worker', required=True, help='Node ID for worker execution.')
@click.option('--rank', type=click.INT)
@click.option('--tag')
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_aggregatetuple(ctx, objective_key, algo_key, in_models_keys, worker, rank, tag,
                       output_format, config, profile, user, verbose):
    """Add aggregatetuple."""
    client = get_client(config, profile, user)
    data = {
        'algo_key': algo_key,
        'objective_key': objective_key,
        'worker': worker,
    }

    if in_models_keys:
        data['in_models_keys'] = in_models_keys

    if rank is not None:
        data['rank'] = rank

    if tag:
        data['tag'] = tag
    res = client.add_aggregatetuple(data)
    printer = printers.get_asset_printer(assets.AGGREGATETUPLE, output_format)
    printer.print(res, is_list=False)


@add.command('composite_traintuple')
@click.option('--objective-key', required=True)
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
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_composite_traintuple(ctx, objective_key, algo_key, dataset_key, data_samples,
                             head_model_key, trunk_model_key, out_trunk_model_permissions, tag,
                             output_format, config, profile, user, verbose):
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

    client = get_client(config, profile, user)
    data = {
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': dataset_key,
        'in_head_model_key': head_model_key,
        'in_trunk_model_key': trunk_model_key,
    }

    if data_samples:
        data['train_data_sample_keys'] = data_samples['keys']

    if out_trunk_model_permissions:
        data['out_trunk_model_permissions'] = out_trunk_model_permissions

    if tag:
        data['tag'] = tag
    res = client.add_composite_traintuple(data)
    printer = printers.get_asset_printer(assets.COMPOSITE_TRAINTUPLE, output_format)
    printer.print(res, is_list=False)


@add.command('testtuple')
@click.option('--dataset-key')
@click.option('--traintuple-key', required=True)
@click.option('--data-samples-path', 'data_samples',
              type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              callback=load_json_from_path)
@click.option('--tag')
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def add_testtuple(ctx, dataset_key, traintuple_key, data_samples, tag,
                  output_format, config, profile, user, verbose):
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
    client = get_client(config, profile, user)
    data = {
        'data_manager_key': dataset_key,
        'traintuple_key': traintuple_key,
    }

    if data_samples:
        data['test_data_sample_keys'] = data_samples['keys']

    if tag:
        data['tag'] = tag
    res = client.add_testtuple(data)
    printer = printers.get_asset_printer(assets.TESTTUPLE, output_format)
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
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def get(ctx, asset_name, asset_key, expand, output_format, config, profile, user, verbose):
    """Get asset definition."""
    expand_valid_assets = (assets.DATASET, assets.TRAINTUPLE, assets.OBJECTIVE, assets.TESTTUPLE,
                           assets.COMPOSITE_TRAINTUPLE, assets.AGGREGATETUPLE, assets.COMPUTE_PLAN)
    if expand and asset_name not in expand_valid_assets:  # fail fast
        raise click.UsageError(
            f'--expand option is available with assets {expand_valid_assets}')

    client = get_client(config, profile, user)
    # method must exist in sdk
    method = getattr(client, f'get_{asset_name.lower()}')
    res = method(asset_key)
    printer = printers.get_asset_printer(asset_name, output_format)
    printer.print(res, profile=profile, expand=expand)


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
@click.option(
    '--is-complex', is_flag=True,
    help=(
        "When using filters using 'OR', the server will return a list of matching assets for each "
        "operand. By default these lists are merged into a single list. When set, this option "
        "disables the lists aggregation."
    ),
)
@click_option_output_format
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def list_(ctx, asset_name, filters, filters_logical_clause, advanced_filters, is_complex,
          output_format, config, profile, user, verbose):
    """List assets."""
    client = get_client(config, profile, user)
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
    res = method(filters, is_complex)
    printer = printers.get_asset_printer(asset_name, output_format)
    printer.print(res, is_list=True)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
]))
@click.argument('asset-key')
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def describe(ctx, asset_name, asset_key, config, profile, user, verbose):
    """Display asset description."""
    client = get_client(config, profile, user)
    # method must exist in sdk
    method = getattr(client, f'describe_{asset_name.lower()}')
    description = method(asset_key)
    renderer = consolemd.Renderer()
    renderer.render(description)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.COMPOSITE_ALGO,
    assets.AGGREGATE_ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
]))
@click.argument('key')
@click.option('--folder', type=click.Path(), help='destination folder',
              default='.')
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def download(ctx, asset_name, key, folder, config, profile, user, verbose):
    """Download asset implementation.

    \b
    - algo: the algo and its dependencies
    - dataset: the opener script
    - objective: the metrics and its dependencies
    """
    client = get_client(config, profile, user)
    # method must exist in sdk
    method = getattr(client, f'download_{asset_name.lower()}')
    res = method(key, folder)
    display(res)


@cli.command()
@click.argument('objective_key')
@click_option_expand
@click_option_output_format
@click.option('--sort',
              type=click.Choice(['asc', 'desc']),
              default='desc',
              show_default=True,
              help='Sort models by highest to lowest perf or vice versa')
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def leaderboard(ctx, objective_key, output_format, expand, sort, config, profile, user, verbose):
    """Display objective leaderboard"""
    client = get_client(config, profile, user)
    leaderboard = client.leaderboard(objective_key, sort=sort)
    printer = printers.get_leaderboard_printer(output_format)
    printer.print(leaderboard, expand=expand)


@cli.command()
@click.argument('algo',
                type=click.Path(exists=True))
@click.option('--train-opener',
              type=click.Path(exists=True, dir_okay=False),
              required=True,
              help='opener.py file to use during training.')
@click.option('--test-opener',
              type=click.Path(exists=True, dir_okay=False),
              required=True,
              help='opener.py file to use during testing.')
@click.option('--metrics',
              type=click.Path(exists=True),
              required=True,
              help='metrics directory or archive to use during both training and testing.')
@click.option('--rank',
              type=click.INT,
              default=0,
              help='will be passed to the algo during training.')
@click.option('--train-data-samples',
              type=click.Path(exists=True, file_okay=False),
              help='directory of data samples directories to use during training.')
@click.option('--test-data-samples',
              type=click.Path(exists=True, file_okay=False),
              help='directory of data samples directories to use during testing.')
@click.option('--inmodel', 'inmodels',
              type=click.Path(exists=True, dir_okay=False),
              multiple=True,
              help='model to use as input during training.')
@click.option('--fake-data-samples',
              is_flag=True,
              help='use fake data samples during both training and testing.')
def run_local(algo, train_opener, test_opener, metrics, rank,
              train_data_samples, test_data_samples, inmodels,
              fake_data_samples):
    """Run local.

    Train and test the algo located in ALGO (directory or archive) locally.

    This command can be used to check that objective, dataset and algo assets
    implementations are compatible.

    It will execute sequentially 4 tasks in docker:

    \b
    - train algo using train data samples
    - get model perf
    - test model using test data samples
    - get model perf

    \b
    It will create several output files:
    - sandbox/model/model
    - sandbox/pred_train/perf.json
    - sandbox/pred_train/pred
    - sandbox/pred_test/perf.json
    - sandbox/pred_test/pred
    """
    if fake_data_samples and (train_data_samples or test_data_samples):
        raise click.BadOptionUsage('--fake-data-samples',
                                   'Options --train-data-samples and --test-data-samples cannot '
                                   'be used if --fake-data-samples is activated')
    if not fake_data_samples and not train_data_samples and not test_data_samples:
        raise click.BadOptionUsage('--fake-data-samples',
                                   'Missing option --fake-data-samples or --test-data-samples '
                                   'and -train-data-samples')
    if not fake_data_samples and train_data_samples and not test_data_samples:
        raise click.BadOptionUsage('--test-data-samples',
                                   'Missing option --test-data-samples')
    if not fake_data_samples and not train_data_samples and test_data_samples:
        raise click.BadOptionUsage('--train-data-samples',
                                   'Missing option --train-data-samples')

    runner.compute(algo_path=algo,
                   train_opener_file=train_opener,
                   test_opener_file=test_opener,
                   metrics_path=metrics,
                   train_data_path=train_data_samples,
                   test_data_path=test_data_samples,
                   fake_data_samples=fake_data_samples,
                   rank=rank,
                   inmodels=inmodels)


@cli.group()
@click.pass_context
def update(ctx):
    """Update asset."""
    pass


@update.command('data_sample')
@click.argument('data_samples', type=click.Path(exists=True, dir_okay=False),
                callback=load_json_from_path, metavar="DATA_SAMPLES_PATH")
@click.option('--dataset-key', required=True)
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def update_data_sample(ctx, data_samples, dataset_key, config, profile, user, verbose):
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
    client = get_client(config, profile, user)
    res = client.link_dataset_with_data_samples(dataset_key, data_samples['keys'])
    display(res)


@update.command('dataset')
@click.argument('dataset-key')
@click.argument('objective-key')
@click_option_config
@click_option_profile
@click_option_user
@click_option_verbose
@click.pass_context
@error_printer
def update_dataset(ctx, dataset_key, objective_key, config, profile, user, verbose):
    """Link dataset with objective."""
    client = get_client(config, profile, user)
    res = client.link_dataset_with_objective(dataset_key, objective_key)
    display(res)


if __name__ == '__main__':
    cli()
