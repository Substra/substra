"""
substra

Usage:
  substra config <url> [<version>] [<user>] [<password>] [--profile=<profile>] [--config=<configuration_file_path>] [-k | --insecure]
  substra list <asset> [<filters>] [--profile=<profile>] [--config=<configuration_file_path>] [--is-complex]  [-v | --verbose]
  substra add <asset> <args> [--profile=<profile>] [--config=<configuration_file_path>] [--dry-run] [-v | --verbose]
  substra register <asset> <args> [--profile=<profile>] [--config=<configuration_file_path>] [--dry-run] [-v | --verbose]
  substra update <asset> <pkhash> <args> [--profile=<profile>] [--config=<configuration_file_path>] [-v | --verbose]
  substra get <asset> <pkhash> [--profile=<profile>] [--config=<configuration_file_path>]  [-v | --verbose]
  substra bulk_update <asset> <args> [--profile=<profile>] [--config=<configuration_file_path>] [-v | --verbose]
  substra path <asset> <pkhash> <path> [--profile=<profile>] [--config=<configuration_file_path>] [-v | --verbose]
  substra create_project (starter_kit | isic) <path>  [-v | --verbose]
  substra run_local <algo-path> [--train-opener=<train_opener_path>] [--test-opener=<test_opener_path>] [--metrics=<metrics_path>] [--rank=<rank>] [--train-data-samples=<train_data_sample_path>] [--test-data-samples=<test_data_sample_path>] [--inmodel=<inmodel_path>...] [--outmodels=<outmodels_path>] [--fake-data-samples] [-v | --verbose]
  substra -h | --help
  substra --version

Options:
  -h --help                                     Show this screen.
  --version                                     Show version.
  -k --insecure                                 Do not verify SSL certificates.
  --profile=<profile>                           Create/Use a (new) profile
  --config=<configuration_file_path>            Path to config file (default ~/.substra)
  -v --verbose                                  Print more information when an error occurs

args                                            Stringified JSON or path to a JSON file

Examples:
  substra config http://127.0.0.1:8000 0.0
  substra config http://127.0.0.1:8000 0.0 user password # basic auth user/password
  substra config http://127.0.0.1:8000 0.0 --profile=owkin --config=/tmp/.substra
  substra get data_manager ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994
  substra list data_manager
  substra list objective '["objective:name:Skin Lesion Classification Challenge", "OR", "dataManager:name:Simplified ISIC 2018"]' --profile=owkin --config=/tmp/.substra
  substra add data_manager '{"name": "liver slide", "data_opener": "./tests/assets/data_manager/opener.py", "type": "images", "description": "./tests/assets/data_manager/description.md", "objective_key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c"}'
  substra add data_manager ./data_manager_definition.json
  substra add data_manager ./data_manager_definition.json --dry-run

  # add data_sample
  substra add data_sample '{"path": "./myzippedfile.zip", "data_manager_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'
  # bulk add data_sample
  substra add data_sample '{"paths": ["./myzippedfile.zip", "./myzippedfile2.zip"], "data_manager_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'

  # register data_sample
  substra register data_sample '{"path": "./my_remote_path", "data_manager_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'
  # bulk register data_sample
  substra register data_sample '{"paths": ["./my_remote_path", "./my_remote_path2"], "data_manager_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'


  # bulk update data_sample
  substra bulk_update data_sample '{"data_sample_keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a", "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"], "data_manager_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"]}'

  # get details path of model
  substra path model 640496cd77521be69122092213c0ab4fb3385250656aed7cd71c42e324f67356 details

Assets available:
  - data_manager (add, update, list and get)
  - data_sample (add, register, bulk add, and bulk_update)
  - objective (add, list and get)
  - algo (add, list and get)
  - model (list, get and path)
  - traintuple (add, list and get)
  - testtuple (add, list and get)

Help:
    You can pass the --config option for defining the configuration file path you want to write/get the configuration.
    Use the --profile option for writing/getting the configuration profile to use.
    Use the --dry-run option when adding an asset for testing the validity of your files

    You can use a `--config /tmp/.substra` for testing for example.
    You can use different profiles for making calls to substrabac. Nice when playing with multiple instances of substrabac.

    For additional help using this tool, please open an issue on the Github repository:
    https://github.com/SubstraFoundation/substra-cli
"""

from docopt import docopt

from . import commands
from . import __version__ as VERSION

COMMANDS_MAPPER = {
    'add': commands.Add,
    'register': commands.Register,
    'bulk_update': commands.BulkUpdate,
    'config': commands.Config,
    'get': commands.Get,
    'list': commands.List,
    'update': commands.Update,
    'run_local': commands.RunLocal,
}


def _find_command(ctx):
    for k, v in ctx.items():
        if k in COMMANDS_MAPPER.keys:
            return COMMANDS_MAPPER[k]
    raise ValueError('Command not found')


def _handle_exception(ctx, exception):
    verbose = ctx.get('--verbose', False)
    if verbose:
        raise exception
    print(str(exception))


def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version=VERSION)
    command_class = _find_command(options)
    command = command_class(options)
    try:
        command.run()
    except Exception as e:
        _handle_exception(options, e)
