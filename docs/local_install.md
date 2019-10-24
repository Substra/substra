# Local install of Substra (macOS; UNIX like system)

This guide will help you to get Substra source code and to start a local instance with 2 organisations: owkin and chu-nantes.

## Dependencies

- docker: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- python 3 (recommended 3.6 or 3.7)
  - it is recommended to use a virtual environment to install Substra packages (for instance [virtualenv](https://virtualenv.pypa.io/en/latest/))
- yarn
- redis server

## Configuration

- docker:
  - on macOS, by default, docker has access only to the user directory.
    - Substra requires access to `/substra`, update accordingly the docker desktop configuration (`Preferences` > `File Sharing`).
    - Ensure also that the docker daemon has enough resources to execute the ML pipeline, for instance: CPUs>1, Memory>4.0 GiB (`Preferences` > `Advanced`).
  - on Linux environment, please refer to this [guide](https://github.com/SubstraFoundation/substra-backend/blob/master/README.md) to configure docker.

- network: map localhost to owkin and chunantes backend hostnames. Edit `/etc/hosts` and add the following lines:

```
127.0.0.1       chunantes.substra-backend
127.0.0.1       owkin.substra-backend
```

## Get source code

- Define a root directory for all your Substra git repositorories (for instance `~/substra`)

```bash
export SUBSTRA_SOURCE=~/substra
mkdir -p $SUBSTRA_SOURCE
cd $SUBSTRA_SOURCE
```

- Clone the following repositories from github and fetch the master branch:
  - hlf-k8s
  - substra-chaincode
  - substra-backend
  - substra-frontend

```bash
# for instance, from github through https connection
git clone -b dev https://github.com/SubstraFoundation/hlf-k8s.git
git clone -b dev https://github.com/SubstraFoundation/substra-chaincode.git
git clone -b dev https://github.com/SubstraFoundation/substra-backend.git
git clone -b dev https://github.com/SubstraFoundation/substra-frontend.git
```

## Install command line interface

- It is recommended to create a python virtual environment to install the client dependencies.

For instance with [virtualenv](https://virtualenv.pypa.io/en/latest/):

```bash
python3 -m venv substra
source substra/bin/activate
```

- Configure access to substra private PIP server. Put in your substra virtual environment path the following pip.conf file (more information [here](https://github.com/SubstraFoundation/substra-cli/blob/master/README.md)):

```
[global]
index-url = https://<user>:<pass>@substra-pypi.owkin.com/simple/
```

- Install Substra python sdk and Substra command line interface.

```
pip install substra
```

- The Substra CLI should have been installed. To check the installation has been successful, launch the `substra --version` command. The following lines should be displayed:

```bash
$ substra --version
1.3.0
```

## Pull substra-tools image from private docker repository

It is required to run the algo, opener and metrics scripts on the substra
platform.

- Install Google Cloud SDK: https://cloud.google.com/sdk/install
- Authenticate with your google account: `gcloud auth login`
- Configure docker to use your google credentials for google based docker registery: `gcloud auth configure-docker`
- Pull image: `docker pull eu.gcr.io/substra-208412/substra-tools`

## Start the Substra network

- Install python scripts dependencies:

```bash
pip install pyyaml
```

- Build the network images and start the containers. To do so, launch the python start.py script:

```bash
cd $SUBSTRA_SOURCE/hlf-k8s; ./bootstrap.sh && python3 python-scripts/start.py --no-backup;
```


## Start the django backend

- Build the backend images, and start the required containers (postgres, rabbitmq, celeryworker, celerybeat and substra-backend):

```bash
cd $SUBSTRA_SOURCE/substra-backend; sh build-docker-images.sh; sh scripts/clean_media.sh; cd docker; python3 start.py -d --no-backup;
```

## Start frontend

- The frontend requires a redis server, start it:

```
redis-server /usr/local/etc/redis.conf
```

- Install dependencies and start the frontend:

```bash
cd $SUBSTRA_SOURCE/substra-frontend
yarn install
yarn start
```

- Go to http://localhost:3000/ in your browser to access the web interface.

## Add some assets to Substra

- Install populate script dependencies:

```bash
pip install termcolor
```

- Execute the populate.py script to add assets to Substra:

```bash
cd $SUBSTRA_SOURCE/substra-backend/
python3 populate.py
```

- Use the cli and the frontend to check that the assets have been added.

## Useful aliases

```
export SUBSTRA_SOURCE=~/substra
alias sbnet-start="cd $SUBSTRA_SOURCE/hlf-k8s/; ./bootstrap.sh && python3 python-scripts/start.py --no-backup; docker rm -f run setup; cd -"
alias sbbac-start="pushd .; cd $SUBSTRA_SOURCE/substra-backend/; sh build-docker-images.sh; sh scripts/clean_media.sh; cd docker; python3 start.py -d --no-backup; popd"
alias sbbac-wait="while ! curl owkin.substra-backend:8000 ; do sleep 2 ; done"
```
