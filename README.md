# Substra

Substra CLI and SDK for interacting with substra platform

## Getting started
To install the command line interface and the python sdk, run the following command:

```sh
python setup.py install
```

## Usage

```sh
substra --help
```

## Documentation

- [Command line interface](docs/cli.md)
- [SDK](docs/sdk.md)

## Autocompletion
To enable Bash completion, you need to put into your .bashrc:

```sh
eval "$(_SUBSTRA_COMPLETE=source substra)"
```

For zsh users add this to your .zshrc:

```sh
eval "$(_SUBSTRA_COMPLETE=source_zsh substra)"
```

From this point onwards, substra command line interface will have autocompletion enabled.

## Contributing
### Setup

To setup the project in development mode, run:

```sh
pip install -e .[test]
```

To run all tests, use the following command:

```sh
python setup.py test
```

### Documentation

To generate the command line interface documentation, run the following command:

```sh
python bin/generate_cli_documentation.py
```

Use the following command to generate the python sdk documentation:

```sh
pydocmd simple substra_sdk_py+ substra_sdk_py.Client+ > docs/api.md
```

Documentation will be available in *docs/* directory.
