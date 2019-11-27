# Local install of Substra using kubernetes and skaffold

This guide will help you run the Substra platform on your machine in development mode, with a 2 organisations setup.

- [Setup](#setup)
  - [1. Get the source code](#1-get-the-source-code)
  - [2. Install Docker and Kubernetes](#2-install-docker-and-kubernetes)
  - [3. Configure Kubernetes](#3-configure-kubernetes)
  - [4. Install skaffold](#4-install-skaffold)
- [Running the platform](#running-the-platform)
- [Login, password and urls](#login-password-and-urls)

## Setup

### 1. Get the source code

You'll need to clone 3 repositories: `hlf-k8s`, `substra-backend` and `substra-front`

Git clone commands:

- hlf-k8s: `git clone git@github.com:SubstraFoundation/hlf-k8s.git`
- substra-backend: `git clone git@github.com:SubstraFoundation/substra-backend.git`
- substra-frontend: `git clone git@github.com:SubstraFoundation/substra-frontend.git`

> Note: if you do not have git on your machine, you can also download the code using these links:
>
> - [hlf-k8s](https://github.com/SubstraFoundation/hlf-k8s/archive/dev.zip)
> - [substra-backend](https://github.com/SubstraFoundation/substra-backend/archive/dev.zip)
> - [substra-frontend](https://github.com/SubstraFoundation/substra-frontend/archive/dev.zip)
>
> Do not forget to unzip the files after download.

### 2. Install Docker and Kubernetes

First of all, download the *Docker desktop* installer from https://www.docker.com/products/docker-desktop. You'll have to create an account there to do so. Then run it to install Docker on your machine.

Once installed, launch Docker and open its "preferences" panel. In the Kubernetes tab, check the `Enable Kubernetes` checkbox.

Kubernetes will take a while to launch the first time, but once it is done, you can move on to configuring it as follow:

### 3. Configure Kubernetes

Using the command line, run first this command:

```sh
helm init
```

Once done, we can configure your machine so that the urls `substra-backend.node-1.com`, `substra-backend.node-2.com`, `substra-frontend.node-1.com` and `substra-frontend.node-2.com` point to your local instance of the platform.

To do so, you'll first need to get the host IP address from container by running:

```sh
docker run -it --rm busybox ping host.docker.internal
```

The output should look like this:

```
Unable to find image 'busybox:latest' locally
latest: Pulling from library/busybox
0f8c40e1270f: Pull complete
Digest: sha256:1303dbf110c57f3edf68d9f5a16c082ec06c4cf7604831669faf2c712260b5a0
Status: Downloaded newer image for busybox:latest
PING host.docker.internal (192.168.65.2): 56 data bytes
64 bytes from 192.168.65.2: seq=0 ttl=37 time=0.426 ms
64 bytes from 192.168.65.2: seq=1 ttl=37 time=1.356 ms
64 bytes from 192.168.65.2: seq=2 ttl=37 time=1.187 ms
64 bytes from 192.168.65.2: seq=3 ttl=37 time=1.870 ms
64 bytes from 192.168.65.2: seq=4 ttl=37 time=3.638 ms
```

With new `64 bytes from 192.168.65.2: seq=4 ttl=37 time=3.638 ms` lines added every second. Hit Ctrl-c to stop it.

Please note that you may not see `192.168.65.2` but another address. In this case, you'll have to update the following commands with your address.

Then run:
```sh
sudo ifconfig lo0 alias 192.168.65.2
```
You'll be asked for your password. Once done, you can check that the command ran successfully by running

```sh
ifconfig lo0
```

The output should look like this:

```
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
	options=1203<RXCSUM,TXCSUM,TXSTATUS,SW_TIMESTAMP>
	inet 127.0.0.1 netmask 0xff000000
	inet6 ::1 prefixlen 128
	inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1
	inet 192.168.65.2 netmask 0xffffff00
	nd6 options=201<PERFORMNUD,DAD>
```

The last step will be to update `/etc/hosts` by adding this new line to it:

```
192.168.65.2 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com
```

Running the following command will do it for you (you'll be asked for your password again):

```sh
echo "192.168.65.2 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" | sudo tee -a /etc/hosts
```

### 4. Install skaffold

On OSX, if you have homebrew installed, just run

```
brew install skaffold
```

If you don't have homebrew installed, then install it first with the following command and then run the above command.

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

## Running the platform

Using the command line, navigate to the `hlf-k8s` folder and run:

```sh
skaffold dev
````

Then in a separate terminal, navigate to the `substra-backend` folder and run:

```sh
skaffold dev
````

Lastly, in a third terminal, navigate to the `substra-frontend` folder and once again run

```sh
skaffold dev
```

The platform will be ready once
- the `hlf-k8s` terminal displays `INFO 003 Installed remotely response:<status:200 payload:"OK" >`:

```
[network-org-2-peer-1-hlf-k8s-chaincode-install-0-4bdd4 fabric-tools] 2019-11-14 09:14:52.070 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
```

- the `backend` terminal displays `"GET /readiness HTTP/1.1" 200 2` and `"GET /liveness HTTP/1.1" 200 2` for both `org-1` and `org2`:

```
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:29] "GET /liveness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:36] "GET /readiness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:29] "GET /liveness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:36] "GET /readiness HTTP/1.1" 200 2
```

- the `frontend` terminal displays:

```
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED ORIGINAL PATH: /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED PARSED PATH: /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] UNCACHABLE ROUTE /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED ORIGINAL PATH: /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED PARSED PATH: /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] UNCACHABLE ROUTE /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] CHUNK NAMES [ 'user/components/index' ]
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] CACHING:  /login
```

## Login, password and urls

Once the platform is running, you can sign in to the two organizations using the default development credentials:

org-1:
- API url: `http://substra-backend.node-1.com`
- Frontend url: `http://substra-frontend.node-1.com`
- Username: `node-1`
- Password: `p@$swr0d44`

org-2:
- API url: `http://substra-backend.node-2.com`
- Frontend url: `http://substra-frontend.node-2.com`
- Username: `node-2`
- Password: `p@$swr0d45`
