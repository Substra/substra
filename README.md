<div align="left">
<a href="https://join.slack.com/t/substra-workspace/shared_invite/zt-1fqnk0nw6-xoPwuLJ8dAPXThfyldX8yA"><img src="https://img.shields.io/badge/chat-on%20slack-blue?logo=slack" /></a> <a href="https://docs.substra.org/"><img src="https://img.shields.io/badge/read-docs-purple?logo=mdbook" /></a>
<br /><br /></div>




<picture>
  <source media="(prefers-color-scheme: dark)" srcset="Substra-logo-white.svg">
  <source media="(prefers-color-scheme: light)" srcset="Substra-logo-colour.svg">
  <img alt="Substra" src="Substra-logo-colour.svg" width="600">
</picture>

Substra is an open source federated learning (FL) software. It enables the training and validation of machine learning models on distributed datasets. It provides a flexible Python interface and a web application to run federated learning training at scale. This specifc reposity is the low-level Python library used to interact with a Substra network.

Substra's main usage is in production environments. It has already been deployed and used by hospitals and biotech companies (see the MELLODDY project for instance). Substra can also be used on a single machine to perform FL simulations and debug code.

Substra was originally developed by [Owkin](https://owkin.com/) and is now hosted by the [Linux Foundation for AI and Data](https://lfaidata.foundation/). Today Owkin is the main contributor to Substra.

Join the discussion on [Slack](https://join.slack.com/t/substra-workspace/shared_invite/zt-1fqnk0nw6-xoPwuLJ8dAPXThfyldX8yA)!


## To start using Substra

Have a look at our [documentation](https://docs.substra.org/).

Try out our [MNIST example](https://docs.substra.org/en/stable/substrafl_doc/examples/index.html#example-to-get-started-using-the-pytorch-interface).

## Support

If you need support, please either raise an issue on Github or ask on [Slack](https://join.slack.com/t/substra-workspace/shared_invite/zt-1fqnk0nw6-xoPwuLJ8dAPXThfyldX8yA).

## Real world use cases

Discover how Substra powers projects solving critical scientific questions in a privacy-preserving way. Read more here.


## Contributing

Substra warmly welcomes any contribution. Feel free to fork the repo and create a pull request.


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

### Documentation generation

To generate the command line interface documentation, sdk and schemas documentation, the `python` version
must be 3.8. Run the following command:

```sh
make doc
```

Documentation will be available in the *references/* directory.
