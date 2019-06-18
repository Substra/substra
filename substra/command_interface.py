import json
import functools
import os

import click
import substra_sdk_py as sb

from substra import __version__
from substra import assets, runner
from substra import config as configuration


def get_client(config_path, profile_name):
    """Initialize substra client from config file and profile name."""
    profile = configuration.load_profile(config_path, profile_name)
    client = sb.Client()
    client.create_config(profile=profile_name, **profile)
    client.set_config(profile_name)
    return client


def load_json(path):
    """Load dict from JSON file."""
    with open(path, 'rb') as fp:
        return json.load(fp)


def load_data_samples_json(path):
    """Load data sample keys from JSON file."""
    data = load_json(path)
    return data['data_sample_keys']


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


def click_option_profile(f):
    """Add profile option to command."""
    return click.option(
        '--profile',
        default='default',
        help='Profile name to use.')(f)


def click_option_config(f):
    """Add config option to command."""
    return click.option(
        '--config',
        type=click.Path(exists=True, resolve_path=True),
        default=os.path.expanduser('~/.substra'),
        help='Config path (default ~/.substra).')(f)


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


# TODO patch client to use asset server name


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
@click_option_config
@click.option('--profile', default='default',
              help='Profile name to add')
@click.option('--insecure', '-k', is_flag=True,
              help='Do not verify SSL certificates')
@click.option('--version', '-v', default='0.0')
@click.option('--user', '-u')
@click.option('--password', '-p')
def add_profile_to_config(url, config, profile, insecure, version, user,
                          password):
    """Add profile to config file."""
    data = {
        'url': url,
        'version': version,
        'insecure': insecure,
        'auth': False,
    }
    if user and password:
        data['auth'] = {
            'user': user,
            'password': password,
        }
    configuration.add_profile(config, profile, data)


@cli.command()
@click.argument('algo_path')
# TODO add helper for parameters
@click.option('--train-opener', type=click.Path(exists=True))
@click.option('--test-opener', type=click.Path(exists=True))
@click.option('--metrics', type=click.Path(exists=True))
@click.option('--rank', type=click.INT, default=0)
@click.option('--train-data-samples', type=click.Path(exists=True))
@click.option('--test-data-samples', type=click.Path(exists=True))
@click.option('--inmodel', type=click.Path(exists=True), multiple=True)
@click.option('--outmodel', type=click.Path())
@click.option('--fake-data-samples', is_flag=True)
def run_local(algo_path, train_opener, test_opener, metrics, rank,
              train_data_samples, test_data_samples, inmodel, outmodel,
              fake_data_samples):
    """Run local."""
    inmodels = inmodel  # multiple option
    # TODO merge runner.setup and runner.compute methods
    config = runner.setup(algo_path,
                          train_opener,
                          test_opener,
                          metrics,
                          train_data_samples,
                          test_data_samples,
                          outmodel)
    runner.compute(config, rank, inmodels, dry_run=fake_data_samples)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('asset-key')
@click.option('--expand', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
@catch_exceptions
def get(ctx, asset_name, asset_key, expand, config, profile):
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
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.DATA_SAMPLE,
    assets.DATASET,
    assets.OBJECTIVE,
    assets.TESTTUPLE,
    assets.TRAINTUPLE,
]))
@click.argument('filters', required=False)
@click.option('--is-complex', is_flag=True)
# TODO explain what's the role of is_complex
@click_option_config
@click_option_profile
@click.pass_context
def _list(ctx, asset_name, filters, is_complex, config, profile):
    """List asset."""
    client = get_client(config, profile)
    res = client.list(asset_name, filters, is_complex)
    display(res)


@cli.command()
@click.argument('asset-name', type=click.Choice([
    assets.ALGO,
    assets.DATASET,
    assets.OBJECTIVE,
]))
@click.argument('key')
@click.option('--folder', type=click.Path(), help='destination folder',
              default='.')
@click_option_config
@click_option_profile
@click.pass_context
def download(ctx, asset_name, key, folder, config, profile):
    """Download asset."""
    client = get_client(config, profile)
    res = client.download(asset_name, key, folder)
    display(res)


@cli.group()
@click.pass_context
def add(ctx):
    """Add asset."""
    pass


@add.command('algo')
@click.argument('path', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_algo(ctx, path, dry_run, config, profile):
    """Add algo."""
    client = get_client(config, profile)
    data = load_json(path)
    res = client.add('algo', data, dry_run)
    display(res)


@add.command('dataset')
@click.argument('path', type=click.Path(exists=True))
@click.option('--objective-key')
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_dataset(ctx, path, objective_key, dry_run, config, profile):
    """Add dataset."""
    client = get_client(config, profile)
    data = load_json(path)
    dict_append_to_optional_field(data, 'objective_keys', objective_key)
    res = client.add('data_manager', data, dry_run)
    display(res)


@add.command('objective')
@click.argument('path', type=click.Path(exists=True))
@click.option('--dataset-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_objective(ctx, path, dataset_key, data_samples_path, dry_run, config,
                  profile):
    """Add objective."""
    client = get_client(config, profile)
    data = load_json(path)
    data['test_data_manager_key'] = dataset_key
    data['test_data_sample_keys'] = load_data_samples_json(data_samples_path)
    res = client.add('data_manager', data, dry_run)
    display(res)


@add.command('data_sample')
@click.argument('path', type=click.Path(exists=True))
@click.option('--local/--remote', 'local', is_flag=True, default=True)
@click.option('--test-only', is_flag=True, default=False)
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_data_sample(ctx, path, local, test_only, dry_run, config, profile):
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
@click.option('--objective-key')
@click.option('--algo-key')
@click.option('--dataset-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_traintuple(ctx, objective_key, algo_key, dataset_key,
                   data_samples_path, dry_run, config, profile):
    """Add traintuple."""
    client = get_client(config, profile)
    data = {
        'algo_key': algo_key,
        'objective_key': objective_key,
        'data_manager_key': dataset_key,
        'train_data_sample_keys': load_data_samples_json(data_samples_path),
    }
    res = client.add('traintuple', data, dry_run)
    display(res)


@add.command('testtuple')
@click.option('--dataset-key')
@click.option('--traintuple-key')
@click.option('--data-samples-path',
              type=click.Path(exists=True, resolve_path=True))
@click.option('--dry-run', is_flag=True)
@click_option_config
@click_option_profile
@click.pass_context
def add_testtuple(ctx, dataset_key, traintuple_key,
                  data_samples_path, dry_run, config, profile):
    """Add testtuple."""
    client = get_client(config, profile)
    data = {
        'data_manager_key': dataset_key,
        'traintuple_key': traintuple_key,
        'test_data_sample_keys': load_data_samples_json(data_samples_path),
    }
    res = client.add(assets.TESTTUPLE, data, dry_run)
    display(res)


@cli.group()
@click.pass_context
def update(ctx):
    """Update asset."""
    pass


@update.command('dataset')
@click.argument('dataset-key')
@click.argument('objective-key')
@click_option_config
@click_option_profile
@click.pass_context
def update_dataset(ctx, dataset_key, objective_key, config, profile):
    """Update dataset."""
    client = get_client(config, profile)
    data = {
        'objective_keys': [objective_key],
    }
    res = client.update('data_manager', dataset_key, data)
    display(res)


@update.command('data-sample')
@click.argument('data-samples-path', type=click.Path(exists=True))
@click.argument('dataset-key')
@click_option_config
@click_option_profile
@click.pass_context
def update_data_sample(ctx, data_samples_path, dataset_key, config, profile):
    """Update data samples."""
    client = get_client(config, profile)
    data = {
        'data_manager_keys': [dataset_key],
        'data_sample_keys': load_data_samples_json(data_samples_path),
    }
    res = client.bulk_update(assets.DATA_SAMPLE, data)
    display(res)


if __name__ == '__main__':
    cli()
