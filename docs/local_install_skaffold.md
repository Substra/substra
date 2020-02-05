# Local install of Substra using Kubernetes and Skaffold

> This is an ongoing document, please feel free to reach us or to raise any issue.

This guide will help you to run the Substra platform on your machine in development mode, with a two organisations setup.

## Index
- [Local install of Substra using Kubernetes and Skaffold](#local-install-of-substra-using-kubernetes-and-skaffold)
  - [Index](#index)
  - [1. Requirements](#1-requirements)
    - [General knowledge](#general-knowledge)
    - [Hardware requirements](#hardware-requirements)
    - [Software requirements](#software-requirements)
      - [1. Kubernetes](#1-kubernetes)
        - [Mac](#mac)
        - [Ubuntu](#ubuntu)
      - [2. Minikube](#2-minikube)
      - [3. Helm](#3-helm)
      - [4. Skaffold](#4-skaffold)
    - [Virtualisation](#virtualisation)
  - [2. Setup](#2-setup)
    - [1. Get the source code](#1-get-the-source-code)
    - [2. Configuration](#2-configuration)
      - [Minikube](#minikube)
      - [Network](#network)
        - [Ubuntu](#ubuntu-1)
        - [Mac](#mac-1)
  - [3. Running the platform](#3-running-the-platform)
    - [Start Substra](#start-substra)
    - [Stop Substra](#stop-substra)
  - [4. Login, password and urls](#4-login-password-and-urls)
    - [Credentials and urls](#credentials-and-urls)
    - [Browser extension](#browser-extension)
    - [Substra CLI config & login](#substra-cli-config--login)
  - [5. Titanic example](#5-titanic-example)
  - [6. Troubleshooting](#6-troubleshooting)
    - [Virtualisation](#virtualisation-1)
    - [Kubectl useful commands](#kubectl-useful-commands)
    - [Minikube useful commands](#minikube-useful-commands)
    - [Tiller](#tiller)
    - [Ongoing issues](#ongoing-issues)
  - [7. Further resources](#7-further-resources)
  - [8. Need help](#8-need-help)
  - [9. Acknowledgements](#9-acknowledgements)
___

When everything is ready, you will be able to start Substra with:
```sh
minikube start --cpus 6 --memory 8192 --disk-size 50g --kubernetes-version='v1.15.4'

skaffold dev # in hlf-k8s, susbtra-backend, substra-frontend repositories
```

## 1. Requirements

### General knowledge

I order to install Substra, it is *recommended* to be confortable with your package manager and to have some basic knowledge of Linux administration and network.

### Hardware requirements

> Please be cautious with the parameters passed to Kubernetes as it might try to use all the allocated resources without regards for your system!

If you wish to comfortably run Substra, it is advised to have:

- At least 30 Go of free space but **50** would really be better!
- **8 Go of RAM** for Kubernetes/Minikube! Be warned, 4 Go won't work. 

### Software requirements

> Note: Please **always** refer to the package provider website before installing any software!

> Note: This setup has been tested on Ubuntu 19.10 & 18.04.3, Linux Mint 19 Cinnamon (4.15.0-45-generic Kernel)

Substra deployment is orchestrated by `Kubernetes` and `Minikube` is a great tool for your local Kubernetes deployments.

`Helm` is a Kubernetes package manager that helps install and manage Kubernetes applications. `Tiller` runs inside the Kubernetes Cluster and manages releases of your charts. Helm has two parts : helm (client) & tiller (server). Charts are Helm packages that contains a package description (`Chart.yaml`) and one or more templates which contain Kubernetes manifest files. Charts can be stored locally or on a distant repository.

`Skaffold` is a program working on top of the Kubernetes configuration that will operate the deployment for you. It relies on the `skaffold.yaml` files that you will find at the root of each repositories.

#### [1. Kubernetes](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

##### Mac

First of all, download the `Docker desktop` installer from https://www.docker.com/products/docker-desktop. You'll have to create an account there to do so. Then run it to install Docker on your machine.

Once installed, launch Docker and open its "preferences" panel. In the Kubernetes tab, check the `Enable Kubernetes` checkbox.

Kubernetes will take a while to launch the first time, but once it is done, you can move on to configuring.

If you don't have `homebrew` installed, please install it first with the following command:

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

##### Ubuntu

Please use **[Kubernetes v1.15](https://kubernetes.io/docs/tasks/tools/install-kubectl/)** (client & server):

```sh
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.0/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
kubectl version --client
```

#### [2. Minikube](https://minikube.sigs.k8s.io/docs/start/)

```sh
# Mac
brew install minikube

# Ubuntu
# Get the executable & install it (Please use the up-to-date version)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_1.6.2.deb && sudo dpkg -i minikube_1.6.2.deb
```

#### [3. Helm](https://helm.sh/)

V3 is not supported yet, please use [Helm v2.16.1](https://github.com/helm/helm/releases/tag/v2.16.1)

```sh
# Mac
# Get the executable
curl -LO https://get.helm.sh/helm-v2.16.1-darwin-amd64.tar.gz
# Extract the downloaded archive
tar xzvf helm-v2.16.1-darwin-amd64.tar.gz
cd darwin-amd64/
# Move the executables to your local bin
sudo mv tiller helm /usr/local/bin/

# Linux (amd64)
# Get the executable
curl -LO https://get.helm.sh/helm-v2.16.1-linux-amd64.tar.gz
# Extract the downloaded archive
tar xzvf helm-v2.16.1-linux-amd64.tar.gz
cd linux-amd64/
# Move the executables to your local bin
sudo mv tiller helm /usr/local/bin/
```

#### [4. Skaffold](https://skaffold.dev/)

```sh
# Mac
brew install skaffold
# Or get the executable
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-darwin-amd64
# Make it executable on your machine
chmod +x skaffold
# Move it to your local bin
sudo mv skaffold /usr/local/bin

# Linux
# Get the executable
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
# Make it executable on your machine
chmod +x skaffold
# Move it to your local bin
sudo mv skaffold /usr/local/bin
```

### Virtualisation

- If you are using [VirtualBox](https://www.virtualbox.org/wiki/Downloads) with Ubuntu, you will have to:
  - install `socat` with the command `sudo apt-get install socat`
  - launch all commands with `sudo`
  - pass the parameter `--vm-driver=none` when starting Minikube (`minikube start...`) 
- Ubuntu:
  - Validate your host virtualisation with the command `virt-host-validate`: <https://linux.die.net/man/1/virt-host-validate>
  - [KVM (Kernel Virtual Machine) installation](https://help.ubuntu.com/community/KVM/Installation#Installation)
  - Required packages: [Ubuntu help](https://help.ubuntu.com/community/KVM/Installation#Install_Necessary_Packages)
  - If you need more information about [libvirt & qemu](https://libvirt.org/drvqemu.html)


## 2. Setup

### 1. Get the source code

You will find the main Substra repository [here](https://github.com/SubstraFoundation/substra), but in order to run the Substra framework, you will need to clone 3 repositories: [hlf-k8s](https://github.com/SubstraFoundation/hlf-k8s) (Hyperledger Fabric), [susbtra-backend](https://github.com/SubstraFoundation/substra-backend) and [substra-frontend](https://github.com/SubstraFoundation/substra-frontend).

The `hlf-k8s` repository is in charge of the initialisation of the [Hyperledger Fabric](https://www.hyperledger.org/projects/fabric) network. By default, it will create an `orderer` and two orgs (`org-1` & `org-2`).

The `substra-backend` is powered by Django and is responsible for, among other things, handling the api endpoints.

The `substra-frontend` will serve a neat interface for the end-users.

Go to the folder where you want to add the repositories and launch this command:

```sh
#!/bin/bash
RepoToClone=(
# https
https://github.com/SubstraFoundation/substra.git
https://github.com/SubstraFoundation/hlf-k8s.git
https://github.com/SubstraFoundation/substra-frontend.git
https://github.com/SubstraFoundation/substra-backend.git

# ssh
# git@github.com:SubstraFoundation/substra.git
# git@github.com:SubstraFoundation/hlf-k8s.git
# git@github.com:SubstraFoundation/substra-backend.git
# git@github.com:SubstraFoundation/substra-frontend.git
)

for repo in ${RepoToClone[@]}
do
    echo "Cloning" $repo
    git clone $repo
done
```

TODO: add script?

> Note: if you do not have git on your machine, you can also download and unzip the code using these links:
> - [hlf-k8s](https://github.com/SubstraFoundation/hlf-k8s/archive/master.zip)
> - [substra-backend](https://github.com/SubstraFoundation/substra-backend/archive/master.zip)
> - [substra-frontend](https://github.com/SubstraFoundation/substra-frontend/archive/master.zip)


### 2. Configuration

#### Minikube

Please enable the ingress minikube module: `minikube addons enables ingress`. You might need to edit `skaffold.yaml` files and set `nginx-ingress.enabled` to `false`.

You can now start Minikube with:

```sh
cd hlf-k8s
# Confortable setup
minikube start --cpus 6 --memory 8192 --disk-size 50g --kubernetes-version='v1.15.4'
# Frugal setup
minikube start --cpus 4 --memory 8192 --disk-size 30g --kubernetes-version='v1.15.4'
# VM setup (Please note that inside the VM, you will to execute all commands with sudo)
sudo minikube start --vm-driver=none --kubernetes-version='v1.15.4'

# first time only
helm init
# or you might need to 
helm init --service-account tiller --upgrade
```

#### Network

##### Ubuntu

```sh
# Append your Kubernetes cluster ip to your system hosts
echo "$(minikube ip) substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" >> /etc/hosts

# Inside a VM you will need to use
echo "$(sudo minikube ip) substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" | sudo tee -a /etc/hosts
```

Example:
```sh
192.168.39.32 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com
```

If you want to customise your configuration,
you can assign the ingress loadbalancer ip to the corresponding url, for example:

```sh
10.111.206.49 substra-backend.node-1.com substra-frontend.node-1.com
10.109.77.31 substra-backend.node-2.com substra-frontend.node-2.com
```

If you to expose another service, you can use something like:

```sh
kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${SERVICE_PORT}:${PORT_WANTED}
```

##### Mac

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

## 3. Running the platform

### Start Substra
Once Minikube is running and Tiller initialised, please go the `hlf-k8s`, `substra-backend` and `substra-frontend` repositories and run `skaffold dev` to start Substra with Skaffold:

```sh
# hlf-k8s
skaffold dev # or skaffold run for detached mode

# substra-backend
skaffold dev

# susbtra-frontend
skaffold dev
```

### Stop Substra

In order to stop Substra, hit `ctrl + c` in each repository. If you want to stop the minikube Kubernetes cluster, you can use `minikube stop` and if you want to remove all the Kubernetes cluster, please use the `minikube delete` command.

Reset your installation (if you've used `skaffold run` to start it) with:

```sh
# run from each repository (hlf-k8s, substra-backend, substra-frontend)
skaffold delete
# or
kubectl rm ns peer-1 peer-2 orderer
# or even
minikube delete
```

The platform will be ready once:
- the `hlf-k8s` terminal displays `INFO 003 Installed remotely response:<status:200 payload:"OK" >`

```sh
[network-org-2-peer-1-hlf-k8s-chaincode-install-0-4bdd4 fabric-tools] 2019-11-14 09:14:52.070 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
```

- the `backend` terminal displays `"GET /readiness HTTP/1.1" 200 2` and `"GET /liveness HTTP/1.1" 200 2` for both `org-1` and `org2`:

```sh
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:29] "GET /liveness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:36] "GET /readiness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:29] "GET /liveness HTTP/1.1" 200 2
[backend-org-1-substra-backend-server-7bd48859c-dr9xj substra-backend] [15/Nov/2019 08:09:36] "GET /readiness HTTP/1.1" 200 2
```

- the `frontend` terminal displays:

```sh
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED ORIGINAL PATH: /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED PARSED PATH: /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] UNCACHABLE ROUTE /
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED ORIGINAL PATH: /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] REQUESTED PARSED PATH: /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] UNCACHABLE ROUTE /login
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] CHUNK NAMES [ 'user/components/index' ]
[substra-frontend-peer-2-substra-frontend-848764cb4c-j7qjc substra-frontend] CACHING:  /login
```

Alternatively, instead of using `skaffold`, you might want to start the `substra-frontend` with [yarn](https://yarnpkg.com/getting-started/install):

Start redis:
```sh 
redis-cli
```

Launch yarn:
```sh
yarn install

API_URL=http://substra-backend.node-2.com yarn start
```

If your browser has problems reaching the requested urls, please have a look at your hosts file with `cat /etc/hosts`.

You might want to separate front and backend addresses, for example:
```sh
# minikube ip
192.168.39.51 substra-backend.node-1.com substra-backend.node-2.com

# localhost
127.0.0.1 substra-frontend.node-1.com substra-frontend.node-2.com
```

You can now head to <http://substra-frontend.node-2.com:3000/> and start to play with Substra!


## 4. Login, password and urls

### Credentials and urls
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

You should find the credentials in the charts: `skaffold.yaml` files or in the `substra-backend/charts/substra-backend/values.yaml`.

### Browser extension

In order to use the backend pages (API) on your browser, you will need to install this extension that will send a special header containing a version:
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/modheader-firefox/)
- [Chrome](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj)

You will then need to:
- Add `Request Header`: `text/html;version=0.0, */*; version=0.0`
- Add `Filters` > `URL Pattern`: `http://susbtra-backend.node-1.com`
- Add `Filters` > `URL Pattern`: `http://susbtra-backend.node-2.com`

Or import this to the extension:

```json
[{"title":"Profile 1","hideComment":true,"headers":[   {"enabled":true,"name":"Accept","value":"text/html;version=0.0, */*; version=0.0","comment":""}],"respHeaders":[],"filters":[{"enabled":true,"type":"urls","urlRegex":"http://substra-backend.node-2.com"},{"enabled":true,"type":"urls","urlRegex":"http://susbtra-backend.node-1.com"}],"urlReplacements":[],"appendMode":false}]
```
See: <https://github.com/SubstraFoundation/substra-backend#testing-with-the-browsable-api>


If you are running the `substra/examples`, you will need to edit the `config.json` as follows:

Change from:
```json
{
  "profile_name": "owkin",
  "url": "http://substra-backend.owkin.xyz:8000",
  "username": "substra",
  "password": "p@$swr0d44"
}
```
To:
```json
{
  "profile_name": "owkin",
  "url": "http://substra-backend.node-1.com:80",
  "username": "node-1",
  "password": "p@$swr0d44"
}
```

See: <https://github.com/SubstraFoundation/substra/blob/master/docs/local_install_skaffold.md#login-password-and-urls>


### Substra CLI config & login

> Note: On Ubuntu you might need to install `keyrings-alt` with `pip install keyrings-alt`; you might even have to `sudo apt-get remove python3-keyrings.alt python-keyrings.alt`.

```sh
# Configuration
substra config -u "node-1" -p 'p@$swr0d44' http://substra-backend.node-1.com

# Login
substra login

# Then you can try
substra --help
# or
substra list traintuple
# or
substra get traintuple HASH
```


## 5. Titanic example

> Note: You don't need to create an account on Kaggle, all the required materials are already provided!

If you want to ensure that everything is working approprietly, you use the examples provided in the [Substra repository](https://github.com/SubstraFoundation/substra/blob/master/examples/titanic/README.md#testing-our-assets)


## 6. Troubleshooting

### Virtualisation

- If you are getting this error about libvirt: `[KVM_CONNECTION_ERROR] machine in unknown state: getting connection: getting domain: error connecting to libvirt socket`. You probably need to install additional package: `sudo apt-get install libvirt-daemon-system`
- You might need to change the owner as well: `sudo chown -R $USER:$USER $HOME/.kube` `sudo chown -R $USER:$USER $HOME/.minikube`; See <https://medium.com/@nieldw/running-minikube-with-vm-driver-none-47de91eab84c>

### Kubectl useful commands

- `kubectl cluster-info`
- `kubectl get all --all-namespaces`
- `kubectl delete ns YOUR_NAMESPACE`

### Minikube useful commands

- `minikube ip`
- `minikube dashboard`
- `minikube tunnel`
- `minikube config view`
- `minikube addons list`
- If you are using microk8s: 
  - `microk8s.status`
  - `microk8s.inspect`

### Tiller

- Tiller might need you to use this command in case of error during init: `helm init --service-account tiller --upgrade`. Otherwise, please have a look here: <https://github.com/SubstraFoundation/substra-backend/pull/1>
- tiller issues: <https://stackoverflow.com/questions/51646957/helm-could-not-find-tiller#51662259>
- After running `skaffold dev` in the `hlf-k8s` repo, in case of error related to the `tempchart` folder, please do `rm -rf tempchart`


### Ongoing issues

- Unknown Host Request Forbidden on node 1...
```sh
kubectl edit deployment --namespace kube-system nginx-ingress-controller

# in spec / container / args 
# ADD 
- --enable-ssl-passthrough
# KO method
```
  - Possible alternative to nginx ingress: https://github.com/helm/charts/tree/master/stable/traefik
  - Possible alternative to fix node-1 not being resolved from Clément:
```sh
minikube addons disable ingress
helm install stable/nginx-ingress \
  --name ingress \
  --namespace kube-system  \
  --set "controller.image.tag=0.27.1"  \
  --set "controller.extraArgs.enable-ssl-passthrough="  \
  --set-string "controller.config.http-redirect-code=301"  \
  --set controller.hostNetwork=true  \
  --set "controller.extraArgs.report-node-internal-ip-address=" \
  --set "controller.image.runAsUser=101"
  ```

## 7. Further resources

- Use [k9s](https://github.com/derailed/k9s):
  - `CTRL + A`
  - `:xray deployments all`
  - `?` for help
  - `/server` then `l` for the logs
  - `y` to see the YAML configuration
- kubectx & kubens: <https://github.com/ahmetb/kubectx#installation>
- Local Kubernetes deployment with minikube: <https://kubernetes.io/blog/2019/03/28/running-kubernetes-locally-on-linux-with-minikube-now-with-kubernetes-1.14-support/>
- Helm: <https://www.linux.com/tutorials/helm-kubernetes-package-manager/>
- Hyperledger Fabric
  - Installation: <https://medium.com/hackernoon/hyperledger-fabric-installation-guide-74065855eca9#c566>
  - Building your first network: <https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html>
- [Awesome Kubernetes list](https://github.com/ramitsurana/awesome-kubernetes#starting-point)
- [Minikube](https://minikube.sigs.k8s.io/) is recommended but you can also use [Microk8s](https://microk8s.io/).
- Use [Firefox Multi-Account Containers](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/) extension to have several simultaneous different logins
- TLDR (*Too Long; Didn't Read*): `sudo apt install tldr`

## 8. Need help

Let's talk:
  - [Create an issue on Github](https://github.com/SubstraFoundation/substra/issues/new)
  - Come to chat with us on [Slack](https://substra-workspace.slack.com/archives/CT54J1U2E)
  - Have a look to the [forum](https://forum.substra.org/)
  - Drop us an [email](mailto:hello@substra.org)
  - Or come meet us *afk* in Paris, Nantes or Limoges!

## 9. Acknowledgements

This amazing piece of software has been developed and open sourced by [Owkin](https://owkin.com/) and its [terrific developers](https://github.com/SubstraFoundation/substra/graphs/contributors). The repositories are now maintained by [SubstraFoundation](https://github.com/SubstraFoundation) and its core contributors and users. Besides, Substra is really excited to welcome new members, feedbacks and contributions, so please, feel free to get in touch with us!
