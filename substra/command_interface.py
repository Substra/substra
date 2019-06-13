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
        type=click.Path(),
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
@click.argument('asset', type=click.Choice([
    assets.ALGO,
    assets.OBJECTIVE,
    assets.DATASET,
    assets.MODEL,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('pkhash')
@click.pass_context
@catch_exceptions
def get(ctx, config, profile, asset, pkhash):
    """Get asset by pkhash."""
    client = get_client(config, profile)
    res = client.get(asset, pkhash)
    display(res)


@cli.command('list')
@option_config
@option_profile
@click.option('--is-complex', is_flag=True)
@click.argument('asset', type=click.Choice([
    assets.ALGO,
    assets.OBJECTIVE,
    assets.DATASET,
    assets.MODEL,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('filters', required=False)
@click.pass_context
def _list(ctx, config, profile, asset, filters, is_complex):
    """List asset."""
    client = get_client(config, profile)
    res = client.list(asset, filters, is_complex)
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


if __name__ == '__main__':
    cli()
