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

You can activate autocompletion by copying this content into the file `/etc/bash_completion.d/substra` of your environment:
```bash
_substra() 
{
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--help -h --version"
    commands="config list add register update get bulk_update path create_project run_local"

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    case ${COMP_CWORD} in
        1)
        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))\
        ;;
    2)
         case ${prev} in
        create_project)
            COMPREPLY=($(compgen -W "starter_kit isic" -- ${cur}))
            ;;
            list)
            COMPREPLY=($(compgen -W "algo objective data_manager model testtuple traintuple" -- ${cur}))
            ;;
            add)
            COMPREPLY=($(compgen -W "algo objective data_sample data_manager testtuple traintuple" -- ${cur}))
            ;;
            register)
            COMPREPLY=($(compgen -W "objective data_sample data_manager" -- ${cur}))
            ;;
            update)
            COMPREPLY=($(compgen -W "data_manager" -- ${cur}))
            ;;
            get)
            COMPREPLY=($(compgen -W "algo objective data_manager model testtuple traintuple" -- ${cur}))
            ;;
            bulk_update)
            COMPREPLY=($(compgen -W "data_sample" -- ${cur}))
            ;;
            path)
            COMPREPLY=($(compgen -W "model" -- ${cur}))
            ;;
        esac
        ;;
    *)
        COMPREPLY=()
        ;;
    esac
}

complete -F _substra substra

```

Then source it with `. /etc/bash_completion`

You can test it by typing `substra l` and then pushing tab key.
Enjoy!
