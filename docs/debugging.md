# Debugging your scripts locally

- [Debugging your scripts locally](#debugging-your-scripts-locally)
  - [Dependencies](#dependencies)
  - [Run your code locally](#run-your-code-locally)
    - [Use assets from a deployed Substra platform and local assets](#use-assets-from-a-deployed-substra-platform-and-local-assets)
    - [Dependency between assets](#dependency-between-assets)
    - [Debugging objectives and algos](#debugging-objectives-and-algos)
      - [Example](#example)

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

### Use assets from a deployed Substra platform and local assets

With this, you gain access to the platform in 'read-only' mode and any asset you create is created locally.

This means that any function to get, describe or download an asset works with assets from the platform and local assets. Functions to
list assets will list the assets from the platform and the local ones.  
Functions that create a new asset (they start with `add`) only create local assets.  
To differentiate between a local asset and a remote one, look at their key (or pkhash): for local assets, it starts with `local_`.

Local assets are saved in-memory, so they are deleted at the end of the script.

### Dependency between assets

Any asset created locally can depend on an asset from the platform or on another local asset:
- a traintuple can use an algo and dataset from the platform
- a testtuple can use an objective from the platform
- etc.

There is one exception: a traintuple, testtuple or any other tuple created locally cannot depend on a tuple from the platform 
or from a compute plan defined on the platform.

Since no data can leave the platform, a task depending on a dataset from the platform uses the fake data generated from the opener. The
number of fake samples generated is equal to the number of samples the task would have used.

### Debugging objectives and algos

The execution is done synchronously, so the script waits for the task in progress to end before continuing.  
The execution of the tuples happens in Docker containers that are spawned on the fly and removed once the execution is done.
If you want access to the container while it runs, you can use [`pdb`](https://docs.python.org/3.6/library/pdb.html#pdb.set_trace) to pause the execution 
until you connect to the container.

#### Example

For example, I want to debug an algo. In the `algo.py` file, in the train function, I put a breakpoint with pdb:

```python
import pdb

class Algo(tools.algo.Algo):

  def train(self, X, y, models, rank):
    pdb.set_trace()
```

I create the algo and a traintuple that depends on it in debug mode. When I add the traintuple to the client, it is immediately executed 
and pauses on the pdb breakpoint.

I can then list the running Docker containers:
```shell
docker ps -a
```

and attach to the right container:
```shell
docker attach algo_{algo_key}
```
where {algo_key} is the key of the algo in Substra.


For a complete example, see the [debugging example](../examples/debugging/README.md).