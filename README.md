<h1><img src="substra-logo.svg" alt="substra" width="200"/></h1>

CLI and SDK for interacting with Substra platform.

[Documentation website](https://doc.substra.ai/)

## Table of contents

- [Table of contents](#table-of-contents)
- [Install](#install)
- [Running the Substra platform locally](#running-the-substra-platform-locally)
- [Usage](#usage)
  - [CLI](#cli)
  - [SDK](#sdk)
- [Documentation](#documentation)
- [Examples](#examples)
- [Contributing](#contributing)
  - [Setup](#setup)
  - [Code formatting](#code-formatting)
  - [Documentation](#documentation-1)
  - [Deploy](#deploy)

## Install

To install the command line interface and the python sdk, run the following command:

```sh
pip install substra
```

To enable Bash completion, you need to put into your .bashrc:

```sh
eval "$(_SUBSTRA_COMPLETE=source substra)"
```

For zsh users add this to your .zshrc:

```sh
eval "$(_SUBSTRA_COMPLETE=source_zsh substra)"
```

From this point onwards, substra command line interface will have autocompletion enabled.

## Running the Substra platform locally

Check out the [open source setup guide](https://doc.substra.ai/setup/local_install_skaffold.html) or the
[close source setup guide](https://github.com/owkin/tech-team/wiki/Deploy-Connect-locally-with-k3s)

Before installing the different components of the platform, please have a look to the [compatibility table](https://connect-docs.owkin.com/en/latest/additional/release.html)

## Usage

Credentials are required for using this tool.

### CLI

```sh
substra --help
```

### SDK

```python
import substra

client = substra.Client()
# enjoy...
```

## Open Source Documentation

- Documentation [website](https://doc.substra.ai)
- Documentation [repository](https://github.com/SubstraFoundation/substra-documentation)
- Chat on [Slack](https://substra-workspace.slack.com)

Interacting with the Substra platform:

- [Command line interface](./references/cli.md)
- [SDK](./references/sdk.md)

Implementing your assets in python (thanks to [the substratools library](https://github.com/substrafoundation/substra-tools))

- [Dataset base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#opener)
- [Algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#algo)
- [Composite algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#compositealgo)
- [Aggregate algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#aggregatealgo)

## Examples

- [Titanic](./examples/titanic/README.md)
- [Cross-validation](./examples/cross_val/README.md)
- [Compute plan](./examples/compute_plan/README.md)
- [Debugging](./examples/debugging/README.md)

## Contributing

### Setup

To setup the project in development mode, run:

```sh
pip install -e ".[dev]"
```

To run all tests, use the following command:

```sh
python setup.py test
```

### Code formatting

You can opt into auto-formatting of code on pre-commit using [Black](https://github.com/psf/black).

This relies on hooks managed by [pre-commit](https://pre-commit.com/), which you can set up as follows.

Install [pre-commit](https://pre-commit.com/), then run:

```sh
pre-commit install
```

### Documentation

To generate the command line interface documentation, sdk and schemas documentation, the `python` version
must be 3.7. Run the following command:

```sh
make doc
```

Documentation will be available in the *references/* directory.

### Deploy

Deployment to pypi.org should be automatic thanks to Travis but if you need to do it manually, here is what you need to do:

```sh
rm -rf dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/* --verbose
```
