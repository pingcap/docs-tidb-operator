---
title: Get Started With TiDB Cluster in Kubernetes
summary: Learn how to deploy TiDB Cluster in TiDB Operator in a Kubernetes cluster.
category: how-to
aliases: ['/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-dind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-kind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-minikube/']
---


# Get Started with TiDB Cluster in Kubernetes

This document explains how to create a simple Kubernetes cluster and use it to do a basic test deployment of TiDB Cluster using TiDB Operator.

> **Warning:**
>
> These deployments are for demonstration puroses only. **Do not use** for qualitifcation or in production!

These are the steps this document follows:
1. [Create a Kubernetes Cluster](#create-a-kubernetes-cluster)
2. [Deploy TiDB Operator](#deploy-tidb-operator)
3. [Deploy TiDB Cluster](#deploy-tidb-cluster)
4. [Connect to TiDB Cluster](#connect-to-tidb).

If you have already created a Kubernetes cluster, you can skip to step 2, [Deploy TiDB Operator](#deploy-tidb-operator).

If you want to do a production-quality deployment, use one of these resources:

+ On public cloud:
    - [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md)
    - [Deploy TiDB on GCP GKE (beta)](deploy-on-gcp-gke.md)
    - [Deploy TiDB on Alibaba Cloud ACK](deploy-on-alibaba-cloud.md)

+ In an existing Kubernetes cluster:
    1. Familiarize yourself with [Prerequisites for TiDB in Kubernetes](prerequisites.md)
    2. Configure the local PV for your Kubernetes cluster to achieve low latency of local storage for TiKV according to [Local PV Configuration](configure-storage-class.md#local-pv-configuration)
    3. Install TiDB Operator in a Kubernetes cluster according to [Deploy TiDB Operator in Kubernetes](deploy-tidb-operator.md)
    4. Deploy your TiDB cluster according to [Deploy TiDB in General Kubernetes](deploy-on-general-kubernetes.md)


## Create a Kubernetes Cluster

This section covers 3 different ways to create a simple Kubernetes cluster that can be used to test TiDB Cluster running under TiDB Operator. Choose whichever best matches your environment or experience level.

- [Using kind](#create-a-kubernetes-cluster-using-kind) (Kubernetes in Docker)
- [Using minikube](#create-a-kubernetes-cluster-using-minikube) (Kubernetes running locally in a VM)
- [Using the Google Cloud Shell](deploy-tidb-from-kubernetes-gke.md) (Kubernetes running in the Google Kubernetes Engine in Google Cloud Platform)

### Create a Kubernetes Cluster Using kind

This tutorial shows how to deploy [TiDB Operator](https://github.com/pingcap/tidb-operator) and a TiDB cluster in Kubernetes on your laptop (Linux or macOS) using .sigs.k8s.io/).

[kind](https://kind) is a tool for running local Kubernetes clusters using Docker containers as cluster nodes. It is developed for testing local Kubernetes clusters. The Kubernetes cluster version depends on the node image that kind uses, and you can specify the image to be used for the nodes and choose any other published version. Refer to [Docker hub](https://hub.docker.com/r/kindest/node/tags) to see available tags.

> **Warning:**
>
> This is for demonstration purposes only. **Do not use** in production!

Before deployment, make sure the following requirements are satisfied:

- [Docker](https://docs.docker.com/install/): version >= 17.03
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl): version >= 1.12
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/): version >= 0.7.0 (the latest version recommended)
- If using Linux, the value of the sysctl parameter [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) should be set to `1`

The following is an example of using `kind` v0.8.1:

{{< copyable "shell-regular" >}}

```shell
kind create cluster
```

Expected output:
```
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.18.2) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Thanks for using kind! 😊
```

Check whether the cluster is successfully created:

{{< copyable "shell-regular" >}}

```shell
kubectl cluster-info
```

Expected output:
```
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

You're now ready to [Deploy TiDB Operator](#deploy-tidb-operator)!

To destroy the Kubernetes cluster, run the following command:

{{< copyable "shell-regular" >}}

``` shell
kind delete cluster
```

### Create a Kubernetes Cluster Using minikube

This document describes how to deploy a TiDB cluster in the [minikube](https://kubernetes.io/docs/setup/minikube/) cluster.

[Minikube](https://kubernetes.io/docs/setup/minikube/) can start a local Kubernetes cluster inside a VM on your laptop. It works on macOS, Linux, and Windows.

> **Warning:**
>
> This is for demonstration purposes only. **Do not use** in production!

Before deployment, make sure the following requirements are satisfied:

- [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/): version 1.0.0+
  - minikube requires a compatible hypervisor; find more information about that in minikube's installation instructions.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl): version >= 1.12

> **Note:**
>
> Although Minikube supports `--vm-driver=none` that uses host docker instead of VM, it is not fully tested with TiDB Operator and may not work. If you want to try TiDB Operator on a system without virtualization support (e.g., on a VPS), you might consider using [kind](deploy-tidb-from-kubernetes-kind.md) instead.

Execute the following command to start a minikube Kubernetes cluster:

```shell
minikube start
```

You should see output like this, with some differences depending on your OS and hypervisor:
```
😄  minikube v1.10.1 on Darwin 10.15.4
✨  Automatically selected the hyperkit driver. Other choices: docker, vmwarefusion
💾  Downloading driver docker-machine-driver-hyperkit:
    > docker-machine-driver-hyperkit.sha256: 65 B / 65 B [---] 100.00% ? p/s 0s
    > docker-machine-driver-hyperkit: 10.90 MiB / 10.90 MiB  100.00% 1.76 MiB p
🔑  The 'hyperkit' driver requires elevated permissions. The following commands will be executed:

    $ sudo chown root:wheel /Users/user/.minikube/bin/docker-machine-driver-hyperkit
    $ sudo chmod u+s /Users/user/.minikube/bin/docker-machine-driver-hyperkit


💿  Downloading VM boot image ...
    > minikube-v1.10.0.iso.sha256: 65 B / 65 B [-------------] 100.00% ? p/s 0s
    > minikube-v1.10.0.iso: 174.99 MiB / 174.99 MiB [] 100.00% 6.63 MiB p/s 27s
👍  Starting control plane node minikube in cluster minikube
💾  Downloading Kubernetes v1.18.2 preload ...
    > preloaded-images-k8s-v3-v1.18.2-docker-overlay2-amd64.tar.lz4: 525.43 MiB
🔥  Creating hyperkit VM (CPUs=2, Memory=4000MB, Disk=20000MB) ...
🐳  Preparing Kubernetes v1.18.2 on Docker 19.03.8 ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "minikube"
```

For Chinese mainland users, you may use local gcr.io mirrors such as `registry.cn-hangzhou.aliyuncs.com/google_containers`.

```shell
minikube start --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers
```

Or you can configure HTTP/HTTPS proxy environments in your Docker:

```shell
# change 127.0.0.1:1086 to your http/https proxy server IP:PORT
minikube start --docker-env https_proxy=http://127.0.0.1:1086 \
  --docker-env http_proxy=http://127.0.0.1:1086
```

> **Note:**
>
> As minikube is running with VMs (default), the `127.0.0.1` is the VM itself, you might want to use your real IP address of the host machine in some cases.

See [minikube setup](https://kubernetes.io/docs/setup/minikube/) for more options to configure your virtual machine and Kubernetes cluster.


Execute this command to check the status of your Kubernetes and make sure `kubectl` can connect to it:

```
kubectl cluster-info
```

Expect this output:
```
Kubernetes master is running at https://192.168.64.2:8443
KubeDNS is running at https://192.168.64.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

You're now ready to [Deploy TiDB Operator](#deploy-tidb-operator)!

To destroy the Kubernetes cluster, run the following command:

{{< copyable "shell-regular" >}}

``` shell
minikube delete
```

## Deploy TiDB Operator


Before proceeding, make sure the following requirements are satisfied:

- A running Kubernetes Cluster that kubectl can connect to
- [Helm](https://helm.sh/docs/intro/install/): Helm 2 (>= Helm 2.16.5) or the latest stable version of Helm 3

1. Install TiDB Operator

    The usage of Helm is a little different depending on whether you're using Helm 2 or Helm 3. Check the version of Helm using `helm version --short`.

    1. If you're using Helm 2, you must set up the server-side component by installing tiller. If you're using Helm 3, skip to the next step.

        Apply the `RBAC` rule required by the `tiller` component in the cluster and install `tiller`:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/tiller-rbac.yaml && \
        helm init --service-account=tiller --upgrade
        ```

        To confirm that the `tiller` Pod is in the `running` state, run the following command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get po -n kube-system -l name=tiller
        ```

        Expected output:
        ```
        NAME                            READY   STATUS    RESTARTS   AGE
        tiller-deploy-b7b9488b5-j6m6p   1/1     Running   0          18s
        ```

        Once you see "1/1" in the "READY" column for the "tidb-deploy" pod, go on to the next step.

    2. Add the PingCAP repository:

        {{< copyable "shell-regular" >}}

        ```shell
        helm repo add pingcap https://charts.pingcap.org/
        ```

        Expected output:
        ```
        "pingcap" has been added to your repositories
        ```

    3. Create a namespace for TiDB Operator

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create namespace tidb-admin
        ```

        Expected output:
        ```
        namespace/tidb-admin created
        ```

    3. Install TiDB Operator

        The `helm install` syntax is slightly different between Helm 2 and Helm 3.

        - Helm 2:

            {{< copyable "shell-regular" >}}

            ```shell
            helm install --namespace tidb-admin --name tidb-operator pingcap/tidb-operator --version v1.1.0
            ```

        - Helm 3:

            {{< copyable "shell-regular" >}}

            ```shell
            helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.1.0
            ```

        In the case of both Helm 2 and Helm 3, the expected output of the `helm install` command is something like this:
        ```
        NAME:   tidb-operator
        LAST DEPLOYED: Thu May 28 15:17:38 2020
        NAMESPACE: tidb-admin
        STATUS: DEPLOYED

        RESOURCES:
        ==> v1/ConfigMap
        NAME                   DATA  AGE
        tidb-scheduler-policy  1     0s

        ==> v1/Deployment
        NAME                     READY  UP-TO-DATE  AVAILABLE  AGE
        tidb-controller-manager  0/1    1           0          0s
        tidb-scheduler           0/1    1           0          0s

        ==> v1/Pod(related)
        NAME                                      READY  STATUS             RESTARTS  AGE
        tidb-controller-manager-6d8d5c6d64-b8lv4  0/1    ContainerCreating  0         0s
        tidb-controller-manager-6d8d5c6d64-b8lv4  0/1    ContainerCreating  0         0s

        ==> v1/ServiceAccount
        NAME                     SECRETS  AGE
        tidb-controller-manager  1        0s
        tidb-scheduler           1        0s

        ==> v1beta1/ClusterRole
        NAME                                   CREATED AT
        tidb-operator:tidb-controller-manager  2020-05-28T22:17:38Z
        tidb-operator:tidb-scheduler           2020-05-28T22:17:38Z

        ==> v1beta1/ClusterRoleBinding
        NAME                                   ROLE                                               AGE
        tidb-operator:kube-scheduler           ClusterRole/system:kube-scheduler                  0s
        tidb-operator:tidb-controller-manager  ClusterRole/tidb-operator:tidb-controller-manager  0s
        tidb-operator:tidb-scheduler           ClusterRole/tidb-operator:tidb-scheduler           0s
        tidb-operator:volume-scheduler         ClusterRole/system:volume-scheduler                0s


        NOTES:
        1. Make sure tidb-operator components are running
           kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
        2. Install CRD
           kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
           kubectl get customresourcedefinitions
        3. Modify tidb-cluster/values.yaml and create a TiDB cluster by installing tidb-cluster charts
           helm install tidb-cluster
        ```

        Confirm that the TiDB Operator components are running with this command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
        ```

        Expected output:
        ```
        NAME                                       READY   STATUS    RESTARTS   AGE
        tidb-controller-manager-6d8d5c6d64-b8lv4   1/1     Running   0          2m22s
        tidb-scheduler-644d59b46f-4f6sb            2/2     Running   0          2m22s
        ```

        As soon as all pods are in "Running" state, proceed to the next step.

2. Install TiDB Operator CRDs:

    TiDB Operator includes a number of Custom Resource Definitions (CRDs) that implement different components of TiDB Cluster.

    Execute this command to install the CRDs into your cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
    ```

    Expected output:
    ```
    customresourcedefinition.apiextensions.k8s.io/tidbclusters.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/backups.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/restores.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/backupschedules.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbmonitors.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbinitializers.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbclusterautoscalers.pingcap.com created
    ```

## Deploy TiDB Cluster

1. Deploy the TiDB Cluster:

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl create namespace tidb-cluster
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-cluster.yaml -n tidb-cluster
    ```

    Expected output:
    ```
    namespace/tidb-cluster created
    tidbcluster.pingcap.com/basic created
    ```

2. Deploy the TiDB cluster monitor:

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-monitor.yaml -n tidb-cluster
    ```

    Expected output:
    ```
    tidbmonitor.pingcap.com/basic created
    ```

3. View the Pod status:

    {{< copyable "shell-regular" >}}

    ``` shell
    watch kubectl get po -n tidb-cluster
    ```

    Expected output:
    ```
    NAME                              READY   STATUS    RESTARTS   AGE
    basic-discovery-6bb656bfd-xl5pb   1/1     Running   0          9m9s
    basic-monitor-5fc8589c89-gvgjj    3/3     Running   0          8m58s
    basic-pd-0                        1/1     Running   0          9m8s
    basic-pd-1                        1/1     Running   0          9m8s
    basic-pd-2                        1/1     Running   1          9m8s
    basic-tidb-0                      2/2     Running   0          7m14s
    basic-tidb-1                      2/2     Running   0          7m14s
    basic-tikv-0                      1/1     Running   0          8m13s
    basic-tikv-1                      1/1     Running   0          8m13s
    basic-tikv-2                      1/1     Running   0          8m13s
    ```

    As soon as you see pods of each type (`-pd`, `-tikv`, and `-tidb`) and all are in the "Running" state, you can hit Ctrl-C to get back to the command line and go on to [connect to your TiDB Cluster](#connect-to-tidb)!

## Connect to TiDB

To connect to TiDB, you'll need a MySQL-compatible command-line client installed on the host where you've used `kubectl`. This can be the `mysql` executable from an installation of MySQL Server, MariaDB Server, Percona Server, or a standalone client executable from your operating system's package repository.

Once the `-tidb` pods are Running, it's time to connect to the cluster.

We'll connect by first forwarding a port from the local host to the TiDB **service** in Kubernetes. First, get a list of services in the tidb-cluster namespace:


{{< copyable "shell-regular" >}}

``` shell
kubectl get svc -n tidb-cluster
```

Expected output:
```
NAME                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
basic-discovery          ClusterIP   10.101.69.5      <none>        10261/TCP            10m
basic-grafana            ClusterIP   10.106.41.250    <none>        3000/TCP             10m
basic-monitor-reloader   ClusterIP   10.99.157.225    <none>        9089/TCP             10m
basic-pd                 ClusterIP   10.104.43.232    <none>        2379/TCP             10m
basic-pd-peer            ClusterIP   None             <none>        2380/TCP             10m
basic-prometheus         ClusterIP   10.106.177.227   <none>        9090/TCP             10m
basic-tidb               ClusterIP   10.99.24.91      <none>        4000/TCP,10080/TCP   8m40s
basic-tidb-peer          ClusterIP   None             <none>        10080/TCP            8m40s
basic-tikv-peer          ClusterIP   None             <none>        20160/TCP            9m39s
```

In this case, the TiDB service is called **basic-tidb**. Use kubectl to forward this port from the local host to the cluster service:


{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward svc/basic-tidb 4000 > pf.out &
```

This command runs in the background and writes its output to a file called `pf.out` so we can continue working in the same shell session.

{{< copyable "shell-regular" >}}

``` shell
mysql -h 127.0.0.1 -P 4000 -u root
```

Expected output:
```
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 76
Server version: 5.7.25-TiDB-v4.0.0 MySQL Community Server (Apache License 2.0)

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```

Here are some commands you can execute after connecting to the cluster to see some of the functionality available in TiDB:

```
mysql> create table hello_world (id int unsigned not null auto_increment primary key, v varchar(32));
Query OK, 0 rows affected (0.17 sec)

mysql> select * from information_schema.tikv_region_status where db_name=database() and table_name='hello_world'\G
*************************** 1. row ***************************
       REGION_ID: 2
       START_KEY: 7480000000000000FF3700000000000000F8
         END_KEY:
        TABLE_ID: 55
         DB_NAME: test
      TABLE_NAME: hello_world
        IS_INDEX: 0
        INDEX_ID: NULL
      INDEX_NAME: NULL
  EPOCH_CONF_VER: 5
   EPOCH_VERSION: 23
   WRITTEN_BYTES: 0
      READ_BYTES: 0
APPROXIMATE_SIZE: 1
APPROXIMATE_KEYS: 0
1 row in set (0.03 sec)
```

```
mysql> select tidb_version()\G
*************************** 1. row ***************************
tidb_version(): Release Version: v4.0.0
Edition: Community
Git Commit Hash: 689a6b6439ae7835947fcaccf329a3fc303986cb
Git Branch: heads/refs/tags/v4.0.0
UTC Build Time: 2020-05-28 01:37:40
GoVersion: go1.13
Race Enabled: false
TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
Check Table Before Drop: false
1 row in set (0.00 sec)
```

```
mysql> select * from information_schema.tikv_store_status\G
*************************** 1. row ***************************
         STORE_ID: 1
          ADDRESS: basic-tikv-1.basic-tikv-peer.tidb-cluster.svc:20160
      STORE_STATE: 0
 STORE_STATE_NAME: Up
            LABEL: null
          VERSION: 4.0.0
         CAPACITY: 58.42GiB
        AVAILABLE: 36.18GiB
     LEADER_COUNT: 6
    LEADER_WEIGHT: 1
     LEADER_SCORE: 6
      LEADER_SIZE: 6
     REGION_COUNT: 21
    REGION_WEIGHT: 1
     REGION_SCORE: 21
      REGION_SIZE: 21
         START_TS: 2020-05-28 22:47:41
LAST_HEARTBEAT_TS: 2020-05-28 22:52:01
           UPTIME: 4m20.455396487s
*************************** 2. row ***************************
         STORE_ID: 4
          ADDRESS: basic-tikv-0.basic-tikv-peer.tidb-cluster.svc:20160
      STORE_STATE: 0
 STORE_STATE_NAME: Up
            LABEL: null
          VERSION: 4.0.0
         CAPACITY: 58.42GiB
        AVAILABLE: 36.18GiB
     LEADER_COUNT: 3
    LEADER_WEIGHT: 1
     LEADER_SCORE: 3
      LEADER_SIZE: 3
     REGION_COUNT: 21
    REGION_WEIGHT: 1
     REGION_SCORE: 21
      REGION_SIZE: 21
         START_TS: 2020-05-28 22:48:21
LAST_HEARTBEAT_TS: 2020-05-28 22:52:01
           UPTIME: 3m40.598302151s
*************************** 3. row ***************************
         STORE_ID: 5
          ADDRESS: basic-tikv-2.basic-tikv-peer.tidb-cluster.svc:20160
      STORE_STATE: 0
 STORE_STATE_NAME: Up
            LABEL: null
          VERSION: 4.0.0
         CAPACITY: 58.42GiB
        AVAILABLE: 36.18GiB
     LEADER_COUNT: 12
    LEADER_WEIGHT: 1
     LEADER_SCORE: 12
      LEADER_SIZE: 12
     REGION_COUNT: 21
    REGION_WEIGHT: 1
     REGION_SCORE: 21
      REGION_SIZE: 21
         START_TS: 2020-05-28 22:47:17
LAST_HEARTBEAT_TS: 2020-05-28 22:52:07
           UPTIME: 4m50.214838934s
3 rows in set (0.01 sec)
```

```
mysql> select * from information_schema.cluster_info\G
*************************** 1. row ***************************
          TYPE: tidb
      INSTANCE: basic-tidb-1.basic-tidb-peer.tidb-cluster.svc:4000
STATUS_ADDRESS: basic-tidb-1.basic-tidb-peer.tidb-cluster.svc:10080
       VERSION: 5.7.25-TiDB-v4.0.0
      GIT_HASH: 689a6b6439ae7835947fcaccf329a3fc303986cb
    START_TIME: 2020-05-28T22:49:17Z
        UPTIME: 4m15.459086883s
*************************** 2. row ***************************
          TYPE: tidb
      INSTANCE: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:4000
STATUS_ADDRESS: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:10080
       VERSION: 5.7.25-TiDB-v4.0.0
      GIT_HASH: 689a6b6439ae7835947fcaccf329a3fc303986cb
    START_TIME: 2020-05-28T22:50:11Z
        UPTIME: 3m21.459090928s
*************************** 3. row ***************************
          TYPE: pd
      INSTANCE: basic-pd:2379
STATUS_ADDRESS: basic-pd:2379
       VERSION: 4.0.0
      GIT_HASH: 56d4c3d2237f5bf6fb11a794731ed1d95c8020c2
    START_TIME: 2020-05-28T22:45:04Z
        UPTIME: 8m28.459091915s
*************************** 4. row ***************************
          TYPE: tikv
      INSTANCE: basic-tikv-1.basic-tikv-peer.tidb-cluster.svc:20160
STATUS_ADDRESS: 0.0.0.0:20180
       VERSION: 4.0.0
      GIT_HASH: 198a2cea01734ce8f46d55a29708f123f9133944
    START_TIME: 2020-05-28T22:47:41Z
        UPTIME: 5m51.45910075s
*************************** 5. row ***************************
          TYPE: tikv
      INSTANCE: basic-tikv-0.basic-tikv-peer.tidb-cluster.svc:20160
STATUS_ADDRESS: 0.0.0.0:20180
       VERSION: 4.0.0
      GIT_HASH: 198a2cea01734ce8f46d55a29708f123f9133944
    START_TIME: 2020-05-28T22:48:21Z
        UPTIME: 5m11.459102648s
*************************** 6. row ***************************
          TYPE: tikv
      INSTANCE: basic-tikv-2.basic-tikv-peer.tidb-cluster.svc:20160
STATUS_ADDRESS: 0.0.0.0:20180
       VERSION: 4.0.0
      GIT_HASH: 198a2cea01734ce8f46d55a29708f123f9133944
    START_TIME: 2020-05-28T22:47:17Z
        UPTIME: 6m15.459103932s
6 rows in set (0.01 sec)
```

