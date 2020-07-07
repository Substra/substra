# Debugging your scripts locally (using the SDK)

- [Debugging your scripts locally (using the SDK)](#debugging-your-scripts-locally)
  - [Dependencies](#dependencies)
  - [Run your code locally](#run-your-code-locally)

## Dependencies

- Docker:
  - Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Ubuntu/Debian: `sudo apt install docker docker-compose`
- Python 3 (recommended 3.6 or 3.7)
  - It is recommended to use a virtual environment to install Substra packages (for instance [virtualenv](https://virtualenv.pypa.io/en/latest/))
- Substra package


## Run your code locally

With this installation, you can write scripts using the [SDK](../references/sdk.md) as you would for a remote exceution and set the client backend as 'local' to run the script locally:

```python
client = substra.Client(backend="local")
```

When it runs locally, there are a few constraints:
- the setup is "one user, one node", so no communication between nodes
- the data is saved in memory, so all the code should be in one script

The execution is done synchronously, so the script waits for the train / predict to end before continuing.
The execution of the tuples happens in Docker containers that are spawned on the fly and removed once the execution is done.
If you want access to the container while it runs, use the [`input`](https://docs.python.org/3.6/library/functions.html#input) function or any function that needs a user input to terminate to pause the execution until you connect to the container.

For an example, see the [local-debugging example](../examples/local_debugging/README.md).