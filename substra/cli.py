"""
substra

Usage:
  substra config <url> [<version>] [<user>] [<password>] [--profile=<profile>] [--config=<configuration_file_path>] [-k | --insecure]
  substra list <entity> [<filters>] [--profile=<profile>] [--config=<configuration_file_path>]
  substra add <entity> (<args>|<json_file) [--profile=<profile>] [--config=<configuration_file_path>]
  substra get <entity> <pkhash> [--profile=<profile>] [--config=<configuration_file_path>]
  substra -h | --help
  substra --version

Options:
  -h --help                                     Show this screen.
  --version                                     Show version.
  -k --insecure                                 Do not verify SSL certificates.
  --profile=<profile>]                          Create/Use a (new) profile
  --config=<configuration_file_path>            Path to config file (default ~/.substra)

Examples:
  substra config http://127.0.0.1:8000 0.0
  substra config http://127.0.0.1:8000 0.0 user password # basic auth user/password
  substra config http://127.0.0.1:8000 0.0 --profile=owkin --config=/tmp/.substra
  substra get dataset ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994
  substra list dataset
  substra list challenge '["challenge:name:Skin Lesion Classification Challenge", "OR", "dataset:name:Simplified ISIC 2018"]' --profile=owkin --config=/tmp/.substra
  substra add dataset '{"name": "liver slide", "data_opener": "./tests/assets/dataset/opener.py", "type": "images", "description": "./tests/assets/dataset/description.md", "permissions": "all", "challenge_key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c"}'
  substra add dataset ./dataset_definition.json

  # add data
  substra add data '{"file": "./myzippedfile.zip", "dataset_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'
  # add data in bulk
  substra add data '{"files": ["./myzippedfile.zip", "./myzippedfile2.zip"], "dataset_keys": ["b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0"], "test_only": false}'


Entities available:
  - dataset
  - data (add, bulk add, list and get only)
  - challenge
  - algo
  - model (list and get only)
  - traintuple

Help:
    You can pass the --config option for defining the configuration file path you want to write/get the configuration.
    Use the --profile variable for writing/getting the configuration profile to use.

    You can use a `--config /tmp/.substra` for testing for example.
    You can use different profiles for making calls to substrabac. Nice when playing with multiple instances of substrabac.

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/substra/substraSDK
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import substra.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(substra.commands, k) and v:
            module = getattr(substra.commands, k)
            substra.commands = getmembers(module, isclass)
            command = [command[1] for command in substra.commands if command[0] not in ('Base', 'Api')][0]
            command = command(options)
            command.run()
