# Local install of Substra (macOS & Ubuntu/Debian)

- [Local install of Substra (macOS & Ubuntu/Debian)](#local-install-of-substra-macos--ubuntudebian)
  - [1. Dependencies](#1-dependencies)
  - [2. Configuration](#2-configuration)
    - [Docker](#docker)
    - [Network](#network)
  - [3. Get source code](#3-get-source-code)
  - [4. Install command line interface](#4-install-command-line-interface)
  - [5. Start Substra](#5-start-substra)
    - [Start the Substra network](#start-the-substra-network)
    - [Start the Django backend](#start-the-django-backend)
    - [Start frontend](#start-frontend)
  - [6. Add some assets to Substra](#6-add-some-assets-to-substra)
  - [7. Useful aliases](#7-useful-aliases)

This guide will help you to get Substra source code and to start a local instance with two nodes: `owkin` and `chunantes`.

## 1. Dependencies

- Docker: 
  - Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Ubuntu/Debian: `sudo apt install docker docker-compose`
- Python 3 (recommended 3.6 or 3.7)
  - It is recommended to use a virtual environment to install Substra packages (for instance [virtualenv](https://virtualenv.pypa.io/en/latest/))
- [Yarn](https://yarnpkg.com/getting-started/install)
- Redis Server:
  - [Download page](https://redis.io/download) 
  - Or just: `sudo apt install redis-server`

## 2. Configuration

### Docker

  - On macOS, by default, docker has access only to the user directory.
    - Substra requires access to a local folder that you can set through the `SUBSTRA_PATH` variable env (defaults to `/tmp/substra`). Make sure the directory of your choice is accessible by updating accordingly the docker desktop configuration (`Preferences` > `File Sharing`).
    - Also ensure that the docker daemon has enough resources to execute the ML pipeline, for instance: CPUs>1, Memory>4.0 GiB (`Preferences` > `Advanced`).
  - On Linux environment, please refer to this [guide](https://github.com/SubstraFoundation/substra-backend/blob/master/README.md) to configure docker.
    - TODO: MOVE this guide here?

### Network

You will need to map your `localhost` to `owkin` and `chunantes` backend hostnames. To do so, please edit the `/etc/hosts` file and add the following lines:

```sh
127.0.0.1       substra-backend.chunantes.xyz
127.0.0.1       substra-backend.owkin.xyz
```

## 3. Get source code

- Define a root directory for all your Substra git repositories, for instance `~/substra`:

```sh
export SUBSTRA_SOURCE=~/substra
mkdir -p $SUBSTRA_SOURCE
cd $SUBSTRA_SOURCE
```

- Clone the following repositories from [Substra's Github](https://github.com/SubstraFoundation):
  - hlf-k8s
  - substra-chaincode
  - substra-backend
  - substra-frontend

```sh
RepoToClone=(
#!/bin/bash
# https
https://github.com/SubstraFoundation/hlf-k8s.git
https://github.com/SubstraFoundation/substra-chaincode.git
https://github.com/SubstraFoundation/substra-backend.git
https://github.com/SubstraFoundation/substra-frontend.git

# ssh
# git@github.com:SubstraFoundation/hlf-k8s.git
# git@github.com:SubstraFoundation/substra-chaincode.git
# git@github.com:SubstraFoundation/substra-backend.git
# git@github.com:SubstraFoundation/substra-frontend.git
)
for repo in ${RepoToClone[@]}
do
    echo "Cloning" $repo
    git clone $repo
done
```
TODO: ADD script?

## 4. Install command line interface

- It is recommended to create a python virtual environment to install the client dependencies.

For instance with [virtualenv](https://virtualenv.pypa.io/en/latest/):

```sh
python3 -m venv substra
source substra/bin/activate
# or source venv/bin/activate.fish if you are an awesome fish shell user :)
```

- Install Substra python sdk and Substra command line interface.

TODO: ADD requirements.txt! & `pip3 install -r requirements.txt`

```sh
pip3 install substra pyyaml termcolor
```

- The Substra CLI should have been installed. To check the installation has been successful, launch the `substra --version` command. The following lines should be displayed:

```sh
substra --version
0.3.0
```

## 5. Start Substra

### Start the Substra network

- Build the network images and start the containers. To do so, launch the python `start.py` script:

> ???Note: for now, `start.py` will only work when your repositories are located at the root of the `home` of your machine (`~/substra`)

```sh
cd $SUBSTRA_SOURCE/hlf-k8s; ./bootstrap.sh && python3 python-scripts/start.py --no-backup;
```

### Start the Django backend

- Build the backend images, and start the required containers (postgres, rabbitmq, celeryworker, celerybeat and substra-backend):

```sh
cd $SUBSTRA_SOURCE/substra-backend; sh build-docker-images.sh; sh scripts/clean_media.sh; cd docker; python3 start.py -d --no-backup;
```

### Start frontend

- The frontend requires a redis server, start it:

```
redis-server /usr/local/etc/redis.conf
```

- Install dependencies and start the frontend:

```sh
cd $SUBSTRA_SOURCE/substra-frontend
yarn install
yarn start
```

You can now go to <http://localhost:3000/> in your browser to access the web interface!

## 6. Add some assets to Substra

- Execute the `populate.py` script to add assets to Substra:

```sh
cd $SUBSTRA_SOURCE/substra-backend/
python3 populate.py
```

You can now use the cli or the frontend to check that the assets have been added.

## 7. Useful aliases

```sh
export SUBSTRA_SOURCE=~/substra

alias sbnet-start="cd $SUBSTRA_SOURCE/hlf-k8s/; ./bootstrap.sh && python3 python-scripts/start.py --no-backup; docker rm -f run setup; cd -"

alias sbbac-start="pushd .; cd $SUBSTRA_SOURCE/substra-backend/; sh build-docker-images.sh; sh scripts/clean_media.sh; cd docker; python3 start.py -d --no-backup; popd"

alias sbbac-wait="while ! curl substra-backend.owkin.xyz:8000 ; do sleep 2 ; done"
```
