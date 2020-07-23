# Debugging your scripts locally (using the SDK)

- [Debugging your scripts locally (using the SDK)](#debugging-your-scripts-locally-using-the-sdk)
  - [Dependencies](#dependencies)
  - [Run your code locally](#run-your-code-locally)

## Dependencies

The required dependencies are:

- Docker:
  - Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Ubuntu/Debian: `sudo apt install docker docker-compose`
- Python 3 (recommended 3.6 or 3.7)
  - It is recommended to use a virtual environment to install Substra packages (for instance [virtualenv](https://virtualenv.pypa.io/en/latest/))
- Substra package

If you want to debug your script using assets from the Substra platform, you also need access to the platform the assets are on.


## Run your code locally

With this installation, you can write scripts using the [SDK](../references/sdk.md) as you would for a remote execution, then
set the `debug` parameter to `True` when creating the client.

```python
client = substra.Client.from_config_file(profile_name="node-1", debug=True)
```

With this, you gain access to the platform in 'read-only' mode and can create assets locally. The assets you create are saved in-memory,
which means they are deleted at the end of the script, so all of your code should run from one script.  
To help differentiate between local and remote assets, the key or pkhash of local assets starts with `local_`.

Also, a traintuple, testtuple or any other tuple created locally cannot depend on a tuple from the platform. They can however
use datasets, algo and objectives from the platform.
Since no data can leave the platform, a task depending on a dataset from the platform uses the fake data generated from the opener. The
number of fake samples generated is equal to the number of samples the task would have used.

The execution is done synchronously, so the script waits for the task in progress to end before continuing.  
The execution of the tuples happens in Docker containers that are spawned on the fly and removed once the execution is done.
If you want access to the container while it runs, use the [`input`](https://docs.python.org/3.6/library/functions.html#input) function or any function that needs a user input to terminate to pause the execution until you connect to the container.

For an example, see the [debugging example](../examples/debugging/README.md).