import json
import functools
import os

import click
import substra_sdk_py as sb

from substra import __version__
from substra import assets
from substra.commands.config import load_profile


def get_client(config_path, profile_name):
    """Initialize substra client from config file and profile name."""
    profile = load_profile(config_path, profile_name)
    client = sb.Client()
    client.create_config(profile=profile_name, **profile)
    client.set_config(profile_name)
    return client


def load_json(path):
    """Load dict from JSON file."""
    with open(path, 'rb') as fp:
        return json.load(fp)


def dict_append_to_optional_field(data, key, value):
    """Append value to a list that may be null."""
    if key in data:
        data[key].append(value)
    else:
        data[key] = [value]


def display(res):
    """Display result."""
    if isinstance(res, dict) or isinstance(res, list):
        res = json.dumps(res, indent=2)
    print(res)


def option_profile(f):
    """Add profile option to command."""
    return click.option(
        '--profile',
        default='default',
        help='Create/use a (new) profile')(f)


def option_config(f):
    """Add config option to command."""
    return click.option(
        '--config',
        type=click.Path(exists=True, resolve_path=True),
        default=os.path.expanduser('~/.substra'),
        help='Config path (default ~/.substra)')(f)


def catch_exceptions(f):
    """Wrapper to properly catch expected exceptions and display it."""
    @functools.wraps(f)
    def new_func(ctx, *args, **kwargs):
        try:
            return f(ctx, *args, **kwargs)

        except click.ClickException:
            raise

        except (sb.exceptions.ConnectionError, sb.exceptions.Timeout) as e:
            raise click.ClickException(str(e))

        except sb.exceptions.HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = e.response.content

            raise click.ClickException(f"Request failed: {e}:\n{error}")

    return new_func


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """Substra Command Line Interface.

    For help using this tool, please open an issue on the Github repository:
    https://github.com/SubstraFoundation/substra-cli
    """
    pass


@cli.command()
@option_config
@option_profile
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.OBJECTIVE,
    assets.DATASET,
    assets.MODEL,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('asset-key')
@click.option('--expand', is_flag=True)
@click.pass_context
@catch_exceptions
def get(ctx, config, profile, asset_name, asset_key, expand):
    """Get asset by key."""
    expand_valid_assets = (assets.DATASET, assets.TRAINTUPLE)
    if expand and asset_name not in expand_valid_assets:  # fail fast
        raise click.UsageError(
            f'--expand option is available with assets {expand_valid_assets}')

    client = get_client(config, profile)
    res = client.get(asset_name, asset_key)

    if expand:
        if asset_name == assets.DATASET:
            # TODO what should we add?
            pass

        elif asset_name == assets.TRAINTUPLE:
            # TODO to get the associated testtuples we could use the
            #      command get model <traintuple_key> but in this case
            #      what's the goal of the get model command?
            res['testtuples'] = None

        else:
            raise AssertionError  # checked previously

    display(res)


@cli.command('list')
@option_config
@option_profile
@click.option('--is-complex', is_flag=True)
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.OBJECTIVE,
    assets.DATASET,
    assets.DATA_SAMPLE,
    assets.MODEL,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('filters', required=False)
@click.pass_context
def _list(ctx, config, profile, asset_name, filters, is_complex):
    """List asset."""
    client = get_client(config, profile)
    res = client.list(asset_name, filters, is_complex)
    display(res)


@cli.group()
@click.pass_context
def add(ctx):
    """Add asset."""
    pass


@add.command('algo')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.argument('path')
@click.pass_context
def add_algo(ctx, config, profile, dry_run, path):
    """Add algo."""
    client = get_client(config, profile)
    data = load_json(path)
    res = client.add('algo', data, dry_run)
    display(res)


@add.command('dataset')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.option('--objective-key')
@click.argument('path')
@click.pass_context
def add_dataset(ctx, config, profile, dry_run, objective_key, path):
    """Add dataset."""
    client = get_client(config, profile)
    data = load_json(path)
    dict_append_to_optional_field(data, 'objective_keys', objective_key)
    res = client.add('data_manager', data, dry_run)
    display(res)


@add.command('objective')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.option('--dataset-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.argument('path')
@click.pass_context
def add_objective(ctx, config, profile, dry_run, dataset_key,
                  data_samples_path, path):
    """Add objective."""
    client = get_client(config, profile)
    data = load_json(path)
    data['test_data_manager_key'] = dataset_key
    # TODO what is the format of data samples path?
    data['test_data_sample_keys'] = load_json(data_samples_path)
    res = client.add('data_manager', data, dry_run)
    display(res)


@add.command('data-sample')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.option('--local/--remote', 'local', is_flag=True, default=True)
@click.option('--test-only', is_flag=True, default=False)
@click.argument('path')
@click.pass_context
def add_data_sample(ctx, config, profile, dry_run, local, test_only, path):
    """Add data sample."""
    client = get_client(config, profile)
    # TODO allow directory of datasamples and path to datasample directly
    # TODO what is the format of data samples path?
    data = load_json(path)
    if test_only:
        data['test_only'] = True
    method = client.register if not local else client.add
    res = method('data_sample', data, dry_run)
    display(res)


@add.command('traintuple')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.option('--objective-key')
@click.option('--algo-key')
@click.option('--dataset-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.pass_context
def add_traintuple(ctx, config, profile, dry_run, objective_key, algo_key,
                   dataset_key, data_samples_path):
    """Add traintuple."""
    client = get_client(config, profile)
    data = {
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': dataset_key,
        # TODO what is the format of data samples path?
        'train_data_sample_keys': load_json(data_samples_path),
    }
    res = client.add('traintuple', data, dry_run)
    display(res)


@add.command('testtuple')
@option_config
@option_profile
@click.option('--dry-run', is_flag=True)
@click.option('--dataset-key')
@click.option('--traintuple-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.pass_context
def add_testtuple(ctx, config, profile, dry_run, dataset_key, traintuple_key,
                  data_samples_path):
    """Add testtuple."""
    client = get_client(config, profile)
    data = {
        'data_manager_key': dataset_key,
        'traintuple_key': traintuple_key,
        # TODO what is the format of data samples path?
        'test_data_sample_keys': load_json(data_samples_path),
    }
    res = client.add(assets.TESTTUPLE, data, dry_run)
    display(res)


@cli.group()
@click.pass_context
def update(ctx):
    """Update asset."""
    pass


@update.command('dataset')
@option_config
@option_profile
@click.argument('dataset-key')
@click.argument('objective-key')
@click.pass_context
def update_dataset(ctx, config, profile, dataset_key, objective_key):
    """Update dataset."""
    client = get_client(config, profile)
    data = {
        'objective_keys': [objective_key],
    }
    res = client.update('data_manager', dataset_key, data)
    display(res)


@update.command('data-sample')
@option_config
@option_profile
@click.argument('data-samples-path')
@click.argument('dataset-key')
@click.pass_context
def update_data_sample(ctx, config, profile, data_samples_path, dataset_key):
    """Update data samples."""
    client = get_client(config, profile)
    data = {
        'data_manager_keys': [dataset_key],
        # TODO what is the format of data samples path?
        'data_sample_keys': load_json(data_samples_path),
    }
    res = client.bulk_update(assets.DATA_SAMPLE, data)
    display(res)


if __name__ == '__main__':
    cli()
