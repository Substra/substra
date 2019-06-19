substra-cli
===========

*Substra CLI for interacting with substrabac*

Getting started
---------------

The substra cli depends on `substra-sdk-py`, this package is private and you will have to update your `pip.conf` for handling it.  
For this you need to have access to `https://substra-pypi.owkin.com/simple/`  
Ask our current Substra Pypi Server Manager for getting an account.  
You will then need to put in your newly created virtualenv path, a `pip.conf` file containing:
```
[global]
index-url = https://<user>:<pass>@substra-pypi.owkin.com/simple/
```


If you've cloned this project, and want to install the library (*and
all development dependencies*), the command you'll want to run is:

    $ pip install -e .[test]

If you'd like to run all tests for this project, you would run the following command:

    $ python setup.py test

This will trigger [py.test](http://pytest.org/latest/), along with its
popular [coverage](https://pypi.python.org/pypi/pytest-cov) plugin.

Usage
-----

	$ substra --help

Autocompletion
--------------

To enable Bash completion, you need to put into your .bashrc:

```bash
eval "$(_SUBSTRA_COMPLETE=source substra)"
```

For zsh users add this to your .zshrc:

```bash
eval "$(_SUBSTRA_COMPLETE=source_zsh substra)"
```

From this point onwards, substra client will have autocompletion enabled.
