# Local installation of Substra using Kubernetes and Skaffold

> This is an ongoing document, please feel free to reach us or to raise any issue.

This guide will help you to run the Substra platform on your machine in development mode, with a two nodes setup.

- [Local installation of Substra using Kubernetes and Skaffold](#local-installation-of-substra-using-kubernetes-and-skaffold)
  - [1. Requirements](#1-requirements)
    - [General knowledge](#general-knowledge)
    - [Hardware requirements](#hardware-requirements)
    - [Software requirements](#software-requirements)
      - [1. Kubernetes](#1-kubernetes)
      - [2. Minikube](#2-minikube)
      - [3. Helm](#3-helm)
      - [4. Skaffold](#4-skaffold)
    - [Virtualization](#virtualization)
  - [2. Setup](#2-setup)
    - [1. Get the source code](#1-get-the-source-code)
    - [2. Configuration](#2-configuration)
      - [Minikube (Ubuntu only)](#minikube-ubuntu-only)
      - [Helm init](#helm-init)
      - [Network](#network)
  - [3. Running the platform](#3-running-the-platform)
    - [Start Substra](#start-substra)
    - [Stop Substra](#stop-substra)
    - [Reset Substra](#reset-substra)
  - [4. Login, password and urls](#4-login-password-and-urls)
    - [Credentials and urls](#credentials-and-urls)
    - [Browser extension](#browser-extension)
    - [Substra CLI config & login](#substra-cli-config--login)
  - [5. Troubleshooting](#5-troubleshooting)
    - [Virtualization issues](#virtualization-issues)
    - [Kubectl useful commands](#kubectl-useful-commands)
    - [Minikube useful commands](#minikube-useful-commands)
    - [Tiller](#tiller)
    - [[WIP] Ongoing issues](#wip-ongoing-issues)
  - [6. Further resources](#6-further-resources)
  - [7. Need help?](#7-need-help)
  - [8. Acknowledgements](#8-acknowledgements)

___

When everything is ready, you will be able to start Substra with:

```sh
# Ubuntu only
minikube start --cpus 6 --memory 8192 --disk-size 50g --kubernetes-version='v1.15.4'

# In 3 different terminal windows, in this order:
# In the repository hlf-k8s
skaffold dev

# In the repository susbtra-backend
skaffold dev

# In the repository substra-frontend
skaffold dev
```

## 1. Requirements

### General knowledge

I order to install Substra, it is *recommended* to be comfortable with your package manager and to have some basic knowledge of Unix (Mac or Ubuntu/Debian) administration and network.

### Hardware requirements

> Please be cautious with the parameters passed to Kubernetes as it might try to use all the allocated resources without regards for your system!

If you wish to comfortably run Substra, it is advised to have:

- **50 GB of free space** as several images need to be pulled.
- **8 GB of RAM** for Kubernetes.

### Software requirements

> Note: Please **always** refer to the package provider website before installing any software!
> Note: This setup has been tested on Ubuntu 19.10, 18.04.3 & Linux Mint 19 Cinnamon (4.15.0-45-generic Kernel)

Substra deployment is orchestrated by `Kubernetes` and `Minikube` is a great tool for your local Kubernetes deployments.

`Helm` is a Kubernetes package manager that helps install and manage Kubernetes applications. `Tiller` runs inside the Kubernetes Cluster and manages releases of your charts. Helm has two parts : helm (client) & tiller (server). Charts are Helm packages that contains a package description (`Chart.yaml`) and one or more templates which contain Kubernetes manifest files. Charts can be stored locally or on a distant repository.

`Skaffold` is a program working on top of the Kubernetes configuration that will operate the deployment for you. It relies on the `skaffold.yaml` files that you will find at the root of each repositories.

#### [1. Kubernetes](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

- Mac

First of all, download the `Docker desktop` installer from <https://www.docker.com/products/docker-desktop>. You'll have to create an account there to do so. Then run it to install Docker on your machine.

Once installed, launch Docker and open its "preferences" panel. In the Kubernetes tab, check the `Enable Kubernetes` checkbox. If you want, you can select minikube from the Docker toolbar and restart Docker.

Kubernetes will take a while to launch the first time, but once it is done, you can move on to configuring.

If you don't have `homebrew` installed, please install it first: <https://brew.sh/>

- Ubuntu

Please use **[Kubernetes v1.15](https://kubernetes.io/docs/tasks/tools/install-kubectl/)** (client & server):

```sh
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.0/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
kubectl version --client
```

#### [2. Minikube](https://minikube.sigs.k8s.io/docs/start/)

```sh
# Ubuntu only
# Get the executable & install it (Please use the up-to-date version)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_1.6.2.deb && sudo dpkg -i minikube_1.6.2.deb
```

#### [3. Helm](https://helm.sh/)

V3 is not supported yet, please use [Helm v2.16.1](https://github.com/helm/helm/releases/tag/v2.16.1) to get Helm and Tiller. Tiller has been removed from v3.

```sh
# Mac
brew install helm@2

# Ubuntu
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

# Ubuntu
# Get the executable
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
# Make it executable on your machine
chmod +x skaffold
# Move it to your local bin
sudo mv skaffold /usr/local/bin
```

### Virtualization

- If you are in a virtualized environment (*within a Virtual Machine*), you will have to:
  - install `socat` with the command `sudo apt-get install socat`
  - launch all commands with `sudo`
  - pass the parameter `--vm-driver=none` when starting Minikube (`minikube start...`)
- If you use Ubuntu (*not in a VM*), you will need to:
  - Validate your host virtualization with the command `virt-host-validate`: <https://linux.die.net/man/1/virt-host-validate>
  - [KVM (Kernel Virtual Machine) installation](https://help.ubuntu.com/community/KVM/Installation#Installation)
  - Required packages: [Ubuntu help](https://help.ubuntu.com/community/KVM/Installation#Install_Necessary_Packages)
  - If you need more information about [libvirt & qemu](https://libvirt.org/drvqemu.html)
- If you use Mac, this virtualization part is already handled for you.

## 2. Setup

### 1. Get the source code

You will find the main Substra repository [here](https://github.com/SubstraFoundation/substra), but in order to run the Substra framework, you will need to clone 3 repositories: [hlf-k8s](https://github.com/SubstraFoundation/hlf-k8s) (Hyperledger Fabric), [susbtra-backend](https://github.com/SubstraFoundation/substra-backend) and [substra-frontend](https://github.com/SubstraFoundation/substra-frontend).

The `hlf-k8s` repository is in charge of the initialization of the [Hyperledger Fabric](https://www.hyperledger.org/projects/fabric) network. By default, it will create an `orderer` and two orgs (`org-1` & `org-2`).

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
>
> - [hlf-k8s](https://github.com/SubstraFoundation/hlf-k8s/archive/master.zip)
> - [substra-backend](https://github.com/SubstraFoundation/substra-backend/archive/master.zip)
> - [substra-frontend](https://github.com/SubstraFoundation/substra-frontend/archive/master.zip)

### 2. Configuration

#### Minikube (Ubuntu only)

> Note: If you are using Mac, this part will be handled by docker desktop for you; you can directly head to the Helm section.

Please enable the ingress minikube module: `minikube addons enables ingress`. You might need to edit `skaffold.yaml` files and set `nginx-ingress.enabled` to `false`.

You can now start Minikube with:

```sh
cd hlf-k8s
# Comfortable setup
minikube start --cpus 6 --memory 8192 --disk-size 50g --kubernetes-version='v1.15.4'
# Frugal setup
minikube start --cpus 4 --memory 8192 --disk-size 30g --kubernetes-version='v1.15.4'
# VM setup (Inside a VM, you will have to execute all commands with sudo)
sudo minikube start --vm-driver=none --kubernetes-version='v1.15.4'
```

#### Helm init

The first time you install Substra, you will need to use:

```sh
helm init
# or
helm init --upgrade
# you might need to use
helm init --service-account tiller --upgrade
```

#### Network

- Ubuntu

```sh
# Append your Kubernetes cluster ip to your system hosts
echo "$(minikube ip) substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" | sudo tee -a /etc/hosts

# Inside a VM, you will need to use
echo "$(sudo minikube ip) substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" | sudo tee -a /etc/hosts
```

Example:

```sh
192.168.39.32 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com
```

If you want to customize your configuration,
you can assign the ingress loadbalancer ip to the corresponding url, for example:

```sh
10.111.206.49 substra-backend.node-1.com substra-frontend.node-1.com
10.109.77.31 substra-backend.node-2.com substra-frontend.node-2.com
```

If you want to expose another service, you can use something like:

```sh
kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${SERVICE_PORT}:${PORT_WANTED}
```

- Mac

Once done, we can configure your machine so that the urls `substra-backend.node-1.com`, `substra-backend.node-2.com`, `substra-frontend.node-1.com` and `substra-frontend.node-2.com` point to your local instance of the platform.

To do so, you'll first need to get the host IP address from container by running:

```sh
docker run -it --rm busybox ping host.docker.internal
```

The output should look like this:

```sh
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

With new `64 bytes from 192.168.65.2: seq=4 ttl=37 time=3.638 ms` lines added every second. Hit `Ctrl-c` to stop it.

Please note that you may not see `192.168.65.2` but another address. In this case, you'll have to update the following commands with your address.

Then run:

```sh
sudo ifconfig lo0 alias 192.168.65.2
```

You'll be asked for your password. Once done, you can check that the command ran successfully by running:

```sh
ifconfig lo0
```

The output should look like this:

```sh
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
options=1203<RXCSUM,TXCSUM,TXSTATUS,SW_TIMESTAMP>
inet 127.0.0.1 netmask 0xff000000
inet6 ::1 prefixlen 128
inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1
inet 192.168.65.2 netmask 0xffffff00
nd6 options=201<PERFORMNUD,DAD>
```

The last step will be to update `/etc/hosts` by adding this new line to it:

```sh
192.168.65.2 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com
```

Running the following command will do it for you (you'll be asked for your password again):

```sh
echo "192.168.65.2 substra-backend.node-1.com substra-frontend.node-1.com substra-backend.node-2.com substra-frontend.node-2.com" | sudo tee -a /etc/hosts
```

## 3. Running the platform

### Start Substra

- For Ubuntu, once Minikube is running and Tiller initialized, please go the `hlf-k8s`, `substra-backend` and `substra-frontend` repositories and run `skaffold dev` to start Substra with Skaffold.
- For Mac, directly head to the tree repositories and start Substra with Skaffold.

Please note that these commands are quite long to be executed and might take a few minutes.

**In 3 different terminal windows, in this order**:

1 In the `hlf-k8s` repository, please run the command `skaffold dev` (or `skaffold run` for detached mode). The platform will be ready once the terminal displays:

```sh
[network-org-2-peer-1-hlf-k8s-chaincode-install-0-4bdd4 fabric-tools] 2019-11-14 09:14:52.070 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
# or
[network-org-2-peer-1-hlf-k8s-channel-join-0-kljgq fabric-tools] 2020-02-10 10:18:02.211 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
# or
[network-org-2-peer-1-hlf-k8s-channel-join-0-kljgq fabric-tools] 2020-02-10 10:18:02.350 UTC [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
```

![status:200 payload:"OK"](/substra/docs/img/start_hlf-k8s.png "status:200 payload:'OK'")

2 In the `substra-backend` repository, please run the command `skaffold dev`. The platform will be ready once the terminal displays:

```sh
[backend-org-2-substra-backend-server-74bb8486fb-nkq6m substra-backend] INFO - 2020-02-10 10:24:42,514 - django.server - "GET /liveness HTTP/1.1" 200 2
# or
[backend-org-1-substra-backend-server-77cf8cb9fd-cwgs6 substra-backend] INFO - 2020-02-10 10:24:51,393 - django.server - "GET /readiness HTTP/1.1" 200 2
```

![django.server readiness](/substra/docs/img/start_backend.png "django.server readiness")

3 In the `susbtra-frontend` repository, please run the command `skaffold dev`. The platform will be ready once the terminal displays:

```sh
[frontend-org-2-substra-frontend-787554fc4b-pmh2g substra-frontend] CACHING:  /login
```

![CACHING Login](/substra/docs/img/start_frontend.png "CACHING Login")

Alternatively, instead of using `skaffold`, you might want to start the `substra-frontend` with [yarn](https://yarnpkg.com/getting-started/install):

Start Redis in one terminal window:

```sh
redis-cli
```

Launch Yarn in another terminal window:

```sh
yarn install

API_URL=http://substra-backend.node-2.com yarn start
```

You will then have to map the frontend urls to your localhost, like this:

```sh
127.0.0.1 substra-frontend.node-1.com substra-frontend.node-2.com
```

You can now head to <http://substra-frontend.node-2.com:3000/> and start to play with Substra!

### Stop Substra

In order to stop Substra, hit `ctrl + c` in each repository. On Ubuntu, if you want to stop the minikube Kubernetes cluster, you can use `minikube stop`.

If you want to restart, you will just need to run again the `skaffold run` command in the 3 repositories.

### Reset Substra

You can reset your installation (if you've used `skaffold run`) with:

```sh
# run from each repository (hlf-k8s, substra-backend, substra-frontend)
skaffold delete
# or
kubectl rm ns peer-1 peer-2 orderer
# On Ubuntu, to remove all the Kubernetes cluster
minikube delete
```

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

TODO: [KO] Or import this to the extension:

```json
[{"title":"Profile 1","hideComment":true,"headers":[   {"enabled":true,"name":"Accept","value":"text/html;version=0.0, */*; version=0.0","comment":""}],"respHeaders":[],"filters":[{"enabled":true,"type":"urls","urlRegex":"http://substra-backend.node-2.com"},{"enabled":true,"type":"urls","urlRegex":"http://susbtra-backend.node-1.com"}],"urlReplacements":[],"appendMode":false}]
```

See: <https://github.com/SubstraFoundation/substra-backend#testing-with-the-browsable-api>

### Substra CLI config & login

> Note 1: Substra works on Python 3+
>
> Note 2: On Ubuntu, if the command `pip3 install substra` fails, you might need to install `keyrings-alt` with `pip3 install keyrings-alt`; you might even have to `sudo apt-get remove python3-keyrings.alt python-keyrings.alt`.
>
> Note 3: If you are working inside a virtualized environment, you probably will have execute to `pip3` commands with `sudo`.

Prepare your Python [virtual environment](https://virtualenv.pypa.io/en/latest/) to install the Python package:

```sh
# Method 1
pip3 install --user virtualenv

virtualenv -p python3 NAME_OF_YOUR_VENV
# or
virtualenv -p $(which python3) NAME_OF_YOUR_VENV
# then activate your new virtual env
source NAME_OF_YOUR_VENV/bin/activate
# or source venv/bin/activate.fish if you are an awesome fish shell user :)
pip3 install substra

# Method 2
sudo apt install python3-venv

python3 -m venv substra_venv
source substra_venv/bin/activate # activate.fish
pip3 install substra

# Method 1 & 2: stop your virtual environment
deactivate
```

Login with the CLI

```sh
# Configuration
substra config -u "node-1" -p 'p@$swr0d44' http://substra-backend.node-1.com

# Login
substra login

# Then you can try
substra list node
# or
substra --help
# or
substra list traintuple
# or
substra get traintuple HASH
```

## 5. Troubleshooting

### Virtualization issues

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

- Tiller might need you to use this command in case of error during init: `helm init --service-account tiller --upgrade`. You can also try to create a service account with `kubectl create serviceaccount --namespace kube-system tiller`Otherwise, please have a look here: <https://github.com/SubstraFoundation/substra-backend/pull/1>
- tiller issues: <https://stackoverflow.com/questions/51646957/helm-could-not-find-tiller#51662259>
- After running `skaffold dev` in the `hlf-k8s` repo, in case of error related to the `tempchart` folder, please do `rm -rf tempchart`

### [WIP] Ongoing issues

- Unknown Host Request Forbidden on node 1...

```sh
kubectl edit deployment --namespace kube-system nginx-ingress-controller

# in spec / container / args
# ADD
# --enable-ssl-passthrough
# KO method
```

- Possible alternative to nginx ingress: <https://github.com/helm/charts/tree/master/stable/traefik>
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

- If you are getting a `403` error only on <http://substra-backend.node-1.com/> and <http://substra-frontend.node-1.com/> with Firefox, please try with another browser...
- Bad certificate issues: `helm list` or `helm list --all`, `helm delete network-org-1-peer-1 --no-hooks` & in k9s `:jobs` and delete orgs + orderer & `helm delete --purge RELEASE_NAME` (ex. `network-org-1-peer-1`). You can then restart `skaffold dev`.
- [WIP] `Self-signed certificate` issues are related to your network provider/admin

## 6. Further resources

- Use [k9s](https://github.com/derailed/k9s):
  - `CTRL + A`
  - `:xray deployments all`
  - `?` for help
  - `/server` then `l` for the logs
  - `:jobs` might be useful to see what is happening behind the scene
  - `y` to see the YAML configuration
- `kubectx` & `kubens`: <https://github.com/ahmetb/kubectx#installation>
- Local Kubernetes deployment with minikube: <https://kubernetes.io/blog/2019/03/28/running-kubernetes-locally-on-linux-with-minikube-now-with-kubernetes-1.14-support/>
- Helm:
  - <https://www.linux.com/tutorials/helm-kubernetes-package-manager/>
  - [Substra Helm charts](https://hub.helm.sh/charts/substra/hlf-k8s)
  - [Helm 2 documentation](https://v2.helm.sh/docs/)
  - [Helm general file structure](https://v2.helm.sh/docs/developing_charts/#the-chart-file-structure)
- Hyperledger Fabric
  - Installation: <https://medium.com/hackernoon/hyperledger-fabric-installation-guide-74065855eca9#c566>
  - Building your first network: <https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html>
- [Awesome Kubernetes list](https://github.com/ramitsurana/awesome-kubernetes#starting-point)
- [Minikube](https://minikube.sigs.k8s.io/) is recommended on Ubuntu but you can also use [Microk8s](https://microk8s.io/).
- Use [Firefox Multi-Account Containers](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/) extension to have several simultaneous different logins
- TLDR (*Too Long; Didn't Read*): `sudo apt install tldr` on Ubuntu or `brew install tldr`
  - `tldr kubectl`
  - `tldr minikube`
  - `tldr helm`
  - `tldr skaffold`

## 7. Need help?

Let's talk:

- [WIP] [Create an issue on Github](https://github.com/SubstraFoundation/substra/issues/new)
- Come chat with us on [Slack](https://substra-workspace.slack.com/archives/CT54J1U2E) (Please join the workspace to be able to join our *help* channel)
- Have a look to the [forum](https://forum.substra.org/)
- Drop us an [email](mailto:help@substra.org)
- Or come meet us *irl* in Paris, Nantes or Limoges!

## 8. Acknowledgements

This amazing piece of software has been developed and open sourced by [Owkin](https://owkin.com/) and its [terrific developers](https://github.com/SubstraFoundation/substra/graphs/contributors). The repositories are now maintained by [Substra Foundation](https://github.com/SubstraFoundation) and its core contributors and users. Besides, Substra is really excited to welcome new members, feedbacks and contributions, so please, feel free to get in touch with us!
