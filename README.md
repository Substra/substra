<h1><img src="substra-logo.svg" alt="substra" width="200"/></h1>

CLI and SDK for interacting with Substra platform.

[Documentation website](https://doc.substra.ai/)

## Table of contents

- [Install](#install)
- [Running the Substra platform locally](#running-the-substra-platform-locally)
- [Usage](#usage)
  - [CLI](#cli)
  - [SDK](#sdk)
- [Documentation](#documentation)
- [Examples](#examples)
- [Compatibility table (close source)](#compatibility-table-close-source)
- [Compatibility table (open source)](#compatibility-table-open-source)
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

Check out the [setup guide](https://doc.substra.ai/setup/local_install_skaffold.html).

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

## Documentation

- Documentation [website](https://doc.substra.ai)
- Documentation [repository](https://github.com/SubstraFoundation/substra-documentation)
- Chat on [Slack](https://substra-workspace.slack.com)

Interacting with the Substra platform:

- [Command line interface](./references/cli.md)
- [SDK](./references/sdk.md)

Implementing your assets in python (thanks to [the substratools library](https://github.com/substrafoundation/substra-tools))

- [Metric base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#metrics)
- [Dataset base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#opener)
- [Algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#algo)
- [Composite algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#compositealgo)
- [Aggregate algo base class](https://github.com/SubstraFoundation/substra-tools/blob/master/docs/api.md#aggregatealgo)

## Examples

- [Titanic](./examples/titanic/README.md)
- [Cross-validation](./examples/cross_val/README.md)
- [Compute plan](./examples/compute_plan/README.md)
- [Debugging](./examples/debugging/README.md)

## Compatibility table (close source)

These sets of versions have been tested for compatilibility:

|  connect  | substra  | connect-chaincode  | connect-backend  | connect-tests  | connect-hlf-k8s  | connect-frontend  | connect-tools |  orchestrator  |connectlib  |
|---|---|---|---|---|---|---| --- | --- | --- |
| |[`0.10.0`](https://github.com/owkin/substra/releases/tag/0.10.0) | [`0.5.0`](https://github.com/owkin/connect-chaincode/releases/tag/0.5.0) | [`0.2.0`](https://github.com/owkin/connect-backend/releases/tag/0.2.0) <br>[`helm chart 3.1.0`](https://core.harbor.tooling.owkin.com/harbor/projects/3/helm-charts/substra-backend/versions/3.1.0) | [`0.7.0`](https://github.com/owkin/connect-tests/releases/tag/0.7.0) | [`0.1.0`](https://github.com/owkin/connect-hlf-k8s/releases/tag/0.1.0) <br>[`helm chart 8.0.0`](https://core.harbor.tooling.owkin.com/harbor/projects/4/helm-charts/hlf-k8s/versions/8.0.0) | [`0.1.0`](https://github.com/owkin/connect-frontend/releases/tag/0.1.0) <br>[`helm chart 0.1.0+bad8dcc`](https://core.harbor.tooling.owkin.com/harbor/projects/5/helm-charts/connect-frontend/versions/0.1.0%2Bbad8dcc) | [`0.7.0`](https://github.com/owkin/connect-tools/releases/tag/0.7.0) | | NA
| 0.2.0 |[`0.11.0`](https://github.com/owkin/substra/releases/tag/0.11.0) | deprecated | [`0.4.0`](https://github.com/owkin/connect-backend/releases/tag/0.4.0) <br>[`helm chart 7.0.0`](https://core.harbor.tooling.owkin.com/harbor/projects/3/helm-charts/substra-backend/versions/7.0.0) | [`0.8.0`](https://github.com/owkin/connect-tests/releases/tag/0.8.0) | [`0.2.0`](https://github.com/owkin/connect-hlf-k8s/releases/tag/0.2.0) <br>[`helm chart 9.1.1`](https://core.harbor.tooling.owkin.com/harbor/projects/4/helm-charts/hlf-k8s/versions/9.1.1) | [`0.3.0`](https://github.com/owkin/connect-frontend/releases/tag/0.3.0) <br>[`helm chart 0.1.0+4c3f3f7`](https://core.harbor.tooling.owkin.com/harbor/projects/5/helm-charts/connect-frontend/versions/0.1.0%2B4c3f3f7) | [`0.9.0`](https://github.com/owkin/connect-tools/releases/tag/0.9.0) | [`0.1.0`](https://github.com/owkin/orchestrator/releases/tag/0.1.0) <br>[`helm chart 2.1.0`](https://core.harbor.tooling.owkin.com/harbor/projects/2/helm-charts/orchestrator/versions/2.1.0) | NA
| 0.3.0 |[`0.13.0`](https://github.com/owkin/substra/releases/tag/0.13.0) | NA | [`0.5.0`](https://github.com/owkin/connect-backend/releases/tag/0.5.0) <br>[`helm chart 12.1.0`](https://core.harbor.tooling.owkin.com/harbor/projects/3/helm-charts/substra-backend/versions/12.1.0) | [`0.9.0`](https://github.com/owkin/connect-tests/releases/tag/0.9.0) | [`0.2.0`](https://github.com/owkin/connect-hlf-k8s/releases/tag/0.2.0) <br>[`helm chart 10.0.0`](https://core.harbor.tooling.owkin.com/harbor/projects/4/helm-charts/hlf-k8s/versions/10.0.0) | [`0.5.0`](https://github.com/owkin/connect-frontend/releases/tag/0.5.0) <br>[`helm chart 0.4.0-unstable+d2d7d94`](https://core.harbor.tooling.owkin.com/harbor/projects/5/helm-charts/connect-frontend/versions/0.4.0-unstable%2Bd2d7d94) | [`0.9.0`](https://github.com/owkin/connect-tools/releases/tag/0.9.0) | [`0.2.0`](https://github.com/owkin/orchestrator/releases/tag/0.2.0) <br>[`helm chart 3.0.2`](https://core.harbor.tooling.owkin.com/harbor/projects/2/helm-charts/orchestrator/versions/3.0.2) | NA
| 0.5.0 |[`0.15.0`](https://github.com/owkin/substra/releases/tag/0.15.0) | NA | [`0.7.0`](https://github.com/owkin/connect-backend/releases/tag/0.7.0) <br>[`helm chart 13.0.5`](https://core.harbor.tooling.owkin.com/harbor/projects/3/helm-charts/substra-backend/versions/13.0.5) | [`0.10.0`](https://github.com/owkin/connect-tests/releases/tag/0.10.0) | [`0.2.0`](https://github.com/owkin/connect-hlf-k8s/releases/tag/0.2.0) <br>[`helm chart 10.0.1`](https://core.harbor.tooling.owkin.com/harbor/projects/4/helm-charts/hlf-k8s/versions/10.0.1) | [`0.6.0`](https://github.com/owkin/connect-frontend/releases/tag/0.6.0) <br>[`helm chart 0.6.0+673680f`](https://core.harbor.tooling.owkin.com/harbor/projects/5/helm-charts/connect-frontend/versions/0.6.0+673680f) | [`0.9.0`](https://github.com/owkin/connect-tools/releases/tag/0.9.0) | [`0.3.0`](https://github.com/owkin/orchestrator/releases/tag/0.3.0) <br>[`helm chart 4.0.1`](https://core.harbor.tooling.owkin.com/harbor/projects/2/helm-charts/orchestrator/versions/4.0.1) | >=[0.3.0](https://github.com/owkin/connectlib/releases/tag/0.3.0), <=[0.4.0](https://github.com/owkin/connectlib/releases/tag/0.4.0)
| 0.4.0 |[`0.14.0`](https://github.com/owkin/substra/releases/tag/0.14.0) | NA | [`0.6.0`](https://github.com/owkin/connect-backend/releases/tag/0.6.0) <br>[`helm chart 13.0.5`](https://core.harbor.tooling.owkin.com/harbor/projects/3/helm-charts/substra-backend/versions/13.0.5) | [`0.10.0`](https://github.com/owkin/connect-tests/releases/tag/0.10.0) | [`0.2.0`](https://github.com/owkin/connect-hlf-k8s/releases/tag/0.2.0) <br>[`helm chart 10.0.1`](https://core.harbor.tooling.owkin.com/harbor/projects/4/helm-charts/hlf-k8s/versions/10.0.1) | [`0.7.0`](https://github.com/owkin/connect-frontend/releases/tag/0.7.0) <br>[`helm chart 0.6.0+673680f`](https://core.harbor.tooling.owkin.com/harbor/projects/5/helm-charts/connect-frontend/versions/0.6.0+673680f) | [`0.9.0`](https://github.com/owkin/connect-tools/releases/tag/0.9.0) | [`0.4.0`](https://github.com/owkin/orchestrator/releases/tag/0.4.0) <br>[`helm chart 4.0.1`](https://core.harbor.tooling.owkin.com/harbor/projects/2/helm-charts/orchestrator/versions/4.0.1) | [0.5.0](https://github.com/owkin/connectlib/releases/tag/0.5.0)

**Adding entries to the compatibility table**

- Please ensure that the command `make test` from [`connect-tests`](https://github.com/owkin/connect-tests/) passes.

## Compatibility table (open source)

These sets of versions have been tested for compatilibility:

| substra  | substra-chaincode  | substra-backend  | substra-tests  | hlf-k8s  | substra-frontend  | substra-tools |
|---|---|---|---|---|---| --- |
| [`0.4.0-alpha.3`](https://github.com/SubstraFoundation/substra/releases/tag/0.4.0-alpha.3) | [`0.0.8-alpha.6`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.8-alpha.6) | [`0.0.12-alpha.13`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.0.12-alpha.13) | [`0.2.0-alpha.1`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.2.0-alpha.1) | [`0.0.11-alpha.1`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.11-alpha.1) | [`0.0.16`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.16) | |
| [`0.4.0-alpha.4`](https://github.com/SubstraFoundation/substra/releases/tag/0.4.0-alpha.4) | [`0.0.8-alpha.9`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.8-alpha.9) | [`0.0.12-alpha.20`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.0.12-alpha.20) | [`0.2.0-alpha.2`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.2.0-alpha.2) | [`0.0.11-alpha.1`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.11-alpha.1) | [`0.0.16`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.16) | |
| [`0.4.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.4.0) | [`0.0.8`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.8) | [`0.0.12`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.0.12) | [`0.2.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.2.0) | [`0.0.11`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.11) | [`0.0.16`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.16) | |
| [`0.5.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.5.0) | [`0.0.8`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.8) | [`0.0.14`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.0.14) | [`0.3.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.3.0) | [`0.0.12`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.12) | [`0.0.16`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.16) | [`0.5.0`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.5.0) |
| [`0.6.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.6.0) | [`0.0.10`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.10) | [`0.0.19`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.0.19) | [`0.4.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.4.0) | [`0.0.12`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.12) | [`0.0.17`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.17) | [`0.5.0`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.5.0) |
| [`0.7.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.7.0) | [`0.0.11`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.11) | [`0.1.2`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.1.2) <br>[`helm chart 1.4.0`](https://artifacthub.io/packages/helm/substra/substra-backend/1.4.0) | [`0.5.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.5.0) | [`0.0.13`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.13) <br>[`helm chart 3.0.1`](https://artifacthub.io/packages/helm/substra/hlf-k8s/3.0.1) | [`0.0.19`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.19) <br>[`helm chart 1.0.0-alpha.2`](https://artifacthub.io/packages/helm/substra/substra-frontend/1.0.0-alpha.2) | [`0.6.1`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.6.1) |
| [`0.7.1`](https://github.com/SubstraFoundation/substra/releases/tag/0.7.1) | [`0.0.11`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.0.11) | [`0.1.3`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.1.3) <br>[`helm chart 1.5.1`](https://artifacthub.io/packages/helm/substra/substra-backend/1.5.1) | [`0.5.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.5.0) | [`0.0.13`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.13) <br>[`helm chart 3.0.1`](https://artifacthub.io/packages/helm/substra/hlf-k8s/3.0.1) | [`0.0.19`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.19) <br>[`helm chart 1.0.0-alpha.2`](https://artifacthub.io/packages/helm/substra/substra-frontend/1.0.0-alpha.2) | [`0.6.1`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.6.1) |
| [`0.8.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.8.0) | [`0.2.0`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.2.0) | [`0.1.6`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.1.6) <br>[`helm chart 1.6.0`](https://artifacthub.io/packages/helm/substra/substra-backend/1.6.0) | [`0.6.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.6.0) | [`0.0.16`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.16) <br>[`helm chart 5.1.0`](https://artifacthub.io/packages/helm/substra/hlf-k8s/5.1.0) | [`0.0.20`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.20) <br>[`helm chart 1.0.0-alpha.2`](https://artifacthub.io/packages/helm/substra/substra-frontend/1.0.0-alpha.2) | [`0.7.0`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.7.0) |
| [`0.8.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.8.0) | [`0.2.2`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.2.2) | [`0.1.9`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.1.9) <br>[`helm chart 1.9.0`](https://artifacthub.io/packages/helm/substra/substra-backend/1.9.0) | [`0.6.0`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.6.0) | [`0.0.16`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.16) <br>[`helm chart 6.2.2`](https://artifacthub.io/packages/helm/substra/hlf-k8s/6.2.2) | [`0.0.20`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.20) <br>[`helm chart 1.0.0-alpha.2`](https://artifacthub.io/packages/helm/substra/substra-frontend/1.0.0-alpha.2) | [`0.7.0`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.7.0) |
 [`0.9.0`](https://github.com/SubstraFoundation/substra/releases/tag/0.9.0) | [`0.3.0`](https://github.com/SubstraFoundation/substra-chaincode/releases/tag/0.3.0) | [`0.1.12`](https://github.com/SubstraFoundation/substra-backend/releases/tag/0.1.12) <br>[`helm chart 2.0.3`](https://artifacthub.io/packages/helm/substra/substra-backend/2.0.3) | [`0.6.1`](https://github.com/SubstraFoundation/substra-tests/releases/tag/0.6.1) | [`0.0.16`](https://github.com/SubstraFoundation/hlf-k8s/releases/tag/0.0.16) <br>[`helm chart 7.0.0`](https://artifacthub.io/packages/helm/substra/hlf-k8s/7.0.0) | [`0.0.20`](https://github.com/SubstraFoundation/substra-frontend/releases/tag/0.0.20) <br>[`helm chart 1.0.0-alpha.2`](https://artifacthub.io/packages/helm/substra/substra-frontend/1.0.0-alpha.2) | [`0.7.0`](https://github.com/SubstraFoundation/substra-tools/releases/tag/0.7.0) |
 [`0.10.0`](https://github.com/owkin/substra/releases/tag/0.10.0) | [`0.5.0`](https://github.com/owkin/connect-chaincode/releases/tag/0.5.0) | [`0.2.0`](https://github.com/owkin/connect-backend/releases/tag/0.2.0) <br>[`helm chart 3.1.0`](TODO) | [`0.7.0`](https://github.com/owkin/connect-tests/releases/tag/0.7.0) | [`0.1.0`](https://github.com/connect/connect-hlf-k8s/releases/tag/0.1.0) <br>[`helm chart 7.0.0`](TODO) | [`0.0.0`](https://github.com/owkin/connect-frontend/releases/tag/0.0.0) <br>[`helm chart 0.0.0`](TODO) | [`0.7.0`](https://github.com/owkin/connect-tools/releases/tag/0.7.0) |

**Adding entries to the compatibility table**

- Please ensure that all the tests from [`substra-tests`](https://github.com/SubstraFoundation/substra-tests/) pass

```sh
cd substra-tests
make test
```

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
