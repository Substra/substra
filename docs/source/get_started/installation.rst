Installation
============

To install the command line interface and the Python SDK, run the following command:

.. code-block:: console

    $ pip install substra

To enable Bash completion, you need to put into your `.bashrc`:

.. code-block:: console

    $ eval "$(_SUBSTRA_COMPLETE=source substra)"

For zsh users add this to your `.zshrc`:

.. code-block:: console

    $ eval "$(_SUBSTRA_COMPLETE=source_zsh substra)"


.. note::

    Substra CLI isn't compatible yet with Windows unless you use the Linux Sub System. Please have a look at those resources:
        - `WSL <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_
        - `Vscode <https://code.visualstudio.com/docs/remote/wsl>`_
        - `Docker <https://docs.docker.com/docker-for-windows/wsl/>`_

From this point onward, substra command line interface will have autocompletion enabled.
