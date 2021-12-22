---
title: Get Started With TiDB Operator in Kubernetes
summary: Learn how to quickly deploy a TiDB cluster in Kubernetes using TiDB Operator.
aliases: ['/docs/tidb-in-kubernetes/dev/get-started/','/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-dind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-kind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-minikube/','/docs/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind/','/docs/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube/','/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind','/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube']
---

# Get Started with TiDB Operator in Kubernetes

This document introduces how to create a simple Kubernetes cluster and use it to deploy a basic test TiDB cluster using TiDB Operator.

> **Warning:**
>
> This document is for demonstration purposes only. **Do not** follow it in production environments. For deployment in production environments, see the instructions in [See also](#see-also).

You can follow these steps to deploy TiDB Operator and a TiDB cluster:

1. [Create a test Kubernetes cluster](#step-1-create-a-test-kubernetes-cluster)
2. [Deploy TiDB Operator](#step-2-deploy-tidb-operator)
3. [Deploy a TiDB cluster and its monitoring services](#step-3-deploy-a-tidb-cluster-and-its-monitoring-services)
4. [Connect to a TiDB cluster](#step-4-connect-to-tidb)
5. [Upgrade a TiDB cluster](#step-5-upgrade-a-tidb-cluster)
6. [Destroy the TiDB cluster and the Kubernetes cluster](#step-6-destroy-the-tidb-cluster-and-the-kubernetes-cluster)

## Step 1. Create a test Kubernetes cluster

This section describes two different ways to create a simple Kubernetes cluster, and then you can use TiDB Operator to deploy a TiDB cluster on it. Choose whichever best matches your environment.

- [Use kind](#create-a-kubernetes-cluster-using-kind) to deploy a Kubernetes cluster in Docker. It is a common and recommended way.
- [Use minikube](#create-a-kubernetes-cluster-using-minikube) to deploy a Kubernetes cluster running locally in a VM.

Alternatively, you can deploy a Kubernetes cluster in Google Kubernetes Engine in Google Cloud Platform using the [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=en/deploy-tidb-from-kubernetes-gke.md).

<SimpleTab>
<div label="kind">

### Create a Kubernetes cluster using kind

This section shows how to deploy a Kubernetes cluster using [kind](https://kind.sigs.k8s.io/).

kind is a popular tool for running local Kubernetes clusters using Docker containers as cluster nodes. See [Docker Hub](https://hub.docker.com/r/kindest/node/tags) to see available tags. The latest version of kind is used by default.

> **Warning:**
>
> The kind cluster is for test purposes only. **Do not use it** in production environments.

Before deployment, make sure the following requirements are satisfied:

- [Docker](https://docs.docker.com/install/): version >= 17.03
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/): version >= 0.8.0
- For Linux, the value of the sysctl parameter [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) should be set to `1`.

The following is an example of using `kind` v0.8.1:

{{< copyable "shell-regular" >}}

```shell
kind create cluster
```

<details>
<summary><font color=Blue>Expected output</font></summary>
<pre><code>
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
</pre></code>
</details>

Check whether the cluster is successfully created:

{{< copyable "shell-regular" >}}

```shell
kubectl cluster-info
```

<details>
<summary><font color=Blue>Expected output</font></summary>
<pre><code>
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
</code></pre>
</details>

You are now ready to deploy TiDB Operator.

</div>

<div label="minikube">

### Create a Kubernetes cluster using minikube

[minikube](https://minikube.sigs.k8s.io/docs/start/) can start a local Kubernetes cluster inside a VM on your computer. It supports macOS, Linux, and Windows.

> **Note:**
>
> Although minikube supports `--vm-driver=none` that uses host Docker instead of VM, it is not fully tested with TiDB Operator and might not work. If you want to try TiDB Operator on a system without virtualization support (for example, on a VPS), you might consider using [kind](#create-a-kubernetes-cluster-using-kind) instead.

#### Prerequisites

Before deployment, make sure the following requirements are satisfied:

- [minikube](https://minikube.sigs.k8s.io/docs/start/): version 1.0.0+ .minikube requires a compatible hypervisor. For details, refer to minikube installation instructions.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12

#### Start a minikube Kubernetes cluster

After minikube is installed, run the following command to start a minikube Kubernetes cluster:

{{< copyable "shell-regular" >}}

```shell
minikube start
```

<details>
<summary><font color=Blue>Expected output</font></summary>
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

</details>

#### Use `kubectl` to interact with the cluster

To interact with the cluster, you can use `kubectl`, which is included as a sub-command in `minikube`. To make the `kubectl` command available, you can either add the following alias definition command to your shell profile, or run the following alias definition command after opening a new shell.

{{< copyable "shell-regular" >}}

```
alias kubectl='minikube kubectl --'
```

Run this command to check the status of Kubernetes and make sure `kubectl` can connect to it:

{{< copyable "shell-regular" >}}

```
kubectl cluster-info
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
Kubernetes master is running at https://192.168.64.2:8443
KubeDNS is running at https://192.168.64.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

</details>

You are now ready to deploy TiDB Operator.

</div>
</SimpleTab>

## Step 2. Deploy TiDB Operator

You need to install TiDB Operator CRDs first, and then install TiDB Operator.

### Install TiDB Operator CRDs

TiDB Operator includes a number of Custom Resource Definitions (CRDs) that implement different components of the TiDB cluster.

Run this command to install the CRDs into your cluster:

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
customresourcedefinition.apiextensions.k8s.io/tidbclusters.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/backups.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/restores.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/backupschedules.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/tidbmonitors.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/tidbinitializers.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/tidbclusterautoscalers.pingcap.com created
```

</details>

> **Note:**
>
> For Kubernetes earlier than 1.16, only v1beta1 CRD is supported, so you need to change `crd.yaml` in the above command to `crd_v1beta1.yaml`.

### Install TiDB Operator

This section describes how to install TiDB Operator using [Helm 3](https://helm.sh/docs/intro/install/).

1. Add the PingCAP repository:

    {{< copyable "shell-regular" >}}

    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

    <details>
    <summary><font color=Blue>Expected output</font></summary>

    ```
    "pingcap" has been added to your repositories
    ```

    </details>

2. Create a namespace for TiDB Operator:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace tidb-admin
    ```

    <details>
    <summary><font color=Blue>Expected output</font></summary>

    ```
    namespace/tidb-admin created
    ```

    </details>

3. Install TiDB Operator

    {{< copyable "shell-regular" >}}

    ```shell
    helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.2.4
    ```

    <details>
    <summary><font color=Blue>Expected output</font></summary>

    ```
    NAME: tidb-operator
    LAST DEPLOYED: Mon Jun  1 12:31:43 2020
    NAMESPACE: tidb-admin
    STATUS: deployed
    REVISION: 1
    TEST SUITE: None
    NOTES:
    Make sure tidb-operator components are running:

        kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
    ```

    </details>

To confirm that the TiDB Operator components are running, run the following command:

{{< copyable "shell-regular" >}}

```shell
kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
NAME                                       READY   STATUS    RESTARTS   AGE
tidb-controller-manager-6d8d5c6d64-b8lv4   1/1     Running   0          2m22s
tidb-scheduler-644d59b46f-4f6sb            2/2     Running   0          2m22s
```

</details>

As soon as all Pods are in the "Running" state, proceed to the next step.

## Step 3. Deploy a TiDB cluster and its monitoring services

This section describes how to deploy a TiDB cluster and its monitoring services.

### Deploy a TiDB cluster

{{< copyable "shell-regular" >}}

``` shell
kubectl create namespace tidb-cluster && \
    kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-cluster.yaml
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
namespace/tidb-cluster created
tidbcluster.pingcap.com/basic created
```

</details>

If you need to deploy a TiDB cluster on ARM64 machines, refer to [Deploy a TiDB Cluster on ARM64 Machines](deploy-cluster-on-arm64.md).

### Deploy TiDB monitoring services

{{< copyable "shell-regular" >}}

``` shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-monitor.yaml
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
tidbmonitor.pingcap.com/basic created
```

</details>

### View the Pod status

{{< copyable "shell-regular" >}}

``` shell
watch kubectl get po -n tidb-cluster
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
NAME                              READY   STATUS    RESTARTS   AGE
basic-discovery-6bb656bfd-xl5pb   1/1     Running   0          9m9s
basic-monitor-5fc8589c89-gvgjj    3/3     Running   0          8m58s
basic-pd-0                        1/1     Running   0          9m8s
basic-tidb-0                      2/2     Running   0          7m14s
basic-tikv-0                      1/1     Running   0          8m13s
```

</details>

Wait until all Pods for all services are started. As soon as you see Pods of each type (`-pd`, `-tikv`, and `-tidb`) are in the "Running" state, you can press <kbd>Ctrl</kbd>+<kbd>C</kbd> to get back to the command line and go on to connect to your TiDB cluster.

## Step 4. Connect to TiDB

Because TiDB supports the MySQL protocol and most of its syntax, you can connect to TiDB using the MySQL client.

### Install the MySQL client

To connect to TiDB, you need a MySQL-compatible client installed on the host where `kubectl` is installed. This can be the `mysql` executable from an installation of MySQL Server, MariaDB Server, Percona Server, or a standalone client executable from the package of your operating system.

### Forward port 4000

You can connect to TiDB by first forwarding a port from the local host to the TiDB **service** in Kubernetes.

First, get a list of services in the `tidb-cluster` namespace:

{{< copyable "shell-regular" >}}

``` shell
kubectl get svc -n tidb-cluster
```

<details>
<summary><font color=Blue>Expected output</font></summary>

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

</details>

In this case, the TiDB **service** is called **basic-tidb**. Run the following command to forward this port from the local host to the cluster:

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-tidb 4000 > pf4000.out &
```

This command runs in the background and writes its output to a file called `pf4000.out`, so you can continue working in the same shell session.

### Connect to the TiDB service

> **Note:**
>
> To connect to TiDB (< v4.0.7) using a MySQL 8.0 client, if the user account has a password, you must explicitly specify `--default-auth=mysql_native_password`. This is because `mysql_native_password` is [no longer the default plugin](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password).

{{< copyable "shell-regular" >}}

``` shell
mysql --comments -h 127.0.0.1 -P 4000 -u root
```

<details>
<summary><font color=Blue>Expected output</font></summary>

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

</details>

After connecting to the cluster, you can run the following commands to verify that some features available in TiDB. Note that some commands require TiDB 4.0 or higher versions. If you have deployed an earlier version, upgrade by consulting the [Upgrade the TiDB cluster](#step-5-upgrade-a-tidb-cluster) section.

<details>
<summary><font color=Blue>Create a `hello_world` table</font></summary>

```sql
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

</details>

<details>
<summary><font color=Blue>Query the TiDB version</font></summary>

```sql
mysql> select tidb_version()\G
*************************** 1. row ***************************
tidb_version(): Release Version: v5.2.1
Edition: Community
Git Commit Hash: cd8fb24c5f7ebd9d479ed228bb41848bd5e97445
Git Branch: heads/refs/tags/v5.2.1
UTC Build Time: 2021-09-08 02:32:56
GoVersion: go1.16.4
Race Enabled: false
TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
Check Table Before Drop: false
1 row in set (0.01 sec)
```

</details>

<details>
<summary><font color=Blue>Query the TiKV store status</font></summary>

```sql
mysql> select * from information_schema.tikv_store_status\G
*************************** 1. row ***************************
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
1 rows in set (0.01 sec)
```

</details>

<details>
<summary><font color=Blue>Query the TiDB cluster information</font></summary>
This command requires TiDB 4.0 or later versions. If you've deployed an earlier version, [upgrade the TiDB cluster](#step-5-upgrade-a-tidb-cluster).

```sql
mysql> select * from information_schema.cluster_info\G
*************************** 1. row ***************************
          TYPE: tidb
      INSTANCE: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:4000
STATUS_ADDRESS: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:10080
       VERSION: 5.7.25-TiDB-v4.0.0
      GIT_HASH: 689a6b6439ae7835947fcaccf329a3fc303986cb
    START_TIME: 2020-05-28T22:50:11Z
        UPTIME: 3m21.459090928s
*************************** 2. row ***************************
          TYPE: pd
      INSTANCE: basic-pd:2379
STATUS_ADDRESS: basic-pd:2379
       VERSION: 4.0.0
      GIT_HASH: 56d4c3d2237f5bf6fb11a794731ed1d95c8020c2
    START_TIME: 2020-05-28T22:45:04Z
        UPTIME: 8m28.459091915s
*************************** 3. row ***************************
          TYPE: tikv
      INSTANCE: basic-tikv-0.basic-tikv-peer.tidb-cluster.svc:20160
STATUS_ADDRESS: 0.0.0.0:20180
       VERSION: 4.0.0
      GIT_HASH: 198a2cea01734ce8f46d55a29708f123f9133944
    START_TIME: 2020-05-28T22:48:21Z
        UPTIME: 5m11.459102648s
3 rows in set (0.01 sec)
```

</details>

### Access Grafana dashboard

You can forward the port for Grafana to access Grafana dashboard locally:

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

You can access Grafana dashboard at <http://localhost:3000> on the host where you run `kubectl`. The default username and password in Grafana are both `admin`. Note that if you want to access Grafana dashboard at <http://localhost:3000> from your browser, you must run `kubectl` on the same host, not in a Docker container or on a remote host.

For more information about monitoring the TiDB cluster in TiDB Operator, refer to [Deploy Monitoring and Alerts for a TiDB Cluster](monitor-a-tidb-cluster.md).

## Step 5. Upgrade a TiDB cluster

TiDB Operator also makes it easy to perform a rolling upgrade of the TiDB cluster. This section describes how to upgrade your TiDB cluster to the "nightly" release.

Before that, you need to get familiar with two `kubectl` sub-commands:

- `kubectl edit` opens a resource specification in an interactive text editor, where an administrator can make changes and save them. If the changes are valid, they'll be propagated to the cluster resources; if they're invalid, they'll be rejected with an error message. Note that not all elements of the specification are validated at this time. It's possible to save changes that may not be applied to the cluster even though they are accepted.

- `kubectl patch` applies a specification change directly to the running cluster resources. There are several different patch strategies, each of which has various capabilities, limitations, and allowed formats.

### Modify the TiDB cluster version

In this case, you can use a JSON merge patch to update the version of the TiDB cluster to "nightly":

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc basic -n tidb-cluster --type merge -p '{"spec": {"version": "nightly"} }'
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
tidbcluster.pingcap.com/basic patched
```

</details>

### Wait for Pods to restart

To follow the progress of the cluster as its components are upgraded, run the following command. You should see some Pods transiting to `Terminating` and then back to `ContainerCreating` and then to `Running`. Pay attention to the value in the `AGE` pod column to see which pods have restarted.

{{< copyable "shell-regular" >}}

```
watch kubectl get po -n tidb-cluster
```

<details>
<summary><font color=Blue>Expected output</font></summary>

```
NAME                              READY   STATUS        RESTARTS   AGE
basic-discovery-6bb656bfd-7lbhx   1/1     Running       0          24m
basic-pd-0                        1/1     Terminating   0          5m31s
basic-tidb-0                      2/2     Running       0          2m19s
basic-tikv-0                      1/1     Running       0          4m13s
```

</details>

### Forward the TiDB service port

After all Pods have been restarted, you can see that the version number of the cluster has changed.

Note that you need to reset any port forwarding you set up in a previous step, because the pods they forwarded to have been destroyed and recreated. If the `kubectl port-forward` process is still running in your shell, end it before forwarding the port again.

{{< copyable "shell-regular" >}}

```
kubectl port-forward -n tidb-cluster svc/basic-tidb 4000 > pf4000.out &
```

### Check the TiDB cluster version

{{< copyable "shell-regular" >}}

```
mysql --comments -h 127.0.0.1 -P 4000 -u root -e 'select tidb_version()\G'
```

<details>
<summary><font color=Blue>Expected output</font></summary>
Note that `nightly` is not a fixed version. Running the command above at different time might return different results.

```
*************************** 1. row ***************************
tidb_version(): Release Version: v5.4.0-alpha-445-g778e188fa
Edition: Community
Git Commit Hash: 778e188fa7af4f48497ff9e05ca6681bf9a5fa16
Git Branch: master
UTC Build Time: 2021-12-17 17:02:49
GoVersion: go1.16.4
Race Enabled: false
TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
Check Table Before Drop: false
```

</details>

## Step 6. Destroy the TiDB cluster and the Kubernetes cluster

After you finish testing, you can destroy the TiDB cluster and the Kubernetes cluster.

### Destroy the TiDB cluster

This section introduces how to destroy the TiDB cluster.

#### Delete the TiDB cluster

{{< copyable "shell-regular" >}}

```shell
kubectl delete tc basic -n tidb-cluster
```

The `tc` in this command is a short name for tidbclusters.

#### Delete TiDB monitoring services

{{< copyable "shell-regular" >}}

```shell
kubectl delete tidbmonitor basic -n tidb-cluster
```

#### Delete PV data

If your deployment has persistent data storage, deleting the TiDB cluster does not remove the data in the cluster. If you do not need the data, run the following commands to clean the data and the dynamically created persistent disks:

{{< copyable "shell-regular" >}}

```shell
kubectl delete pvc -n tidb-cluster -l app.kubernetes.io/instance=basic,app.kubernetes.io/managed-by=tidb-operator && \
kubectl get pv -l app.kubernetes.io/namespace=tidb-cluster,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=basic -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```

#### Delete namespaces

To make sure there are no lingering resources, delete the namespace used for your TiDB cluster.

{{< copyable "shell-regular" >}}

```shell
kubectl delete namespace tidb-cluster
```

#### Stop `kubectl` port forwarding

If you still have running `kubectl` processes that are forwarding ports, end them:

{{< copyable "shell-regular" >}}

```shell
pgrep -lfa kubectl
```

### Destroy the Kubernetes cluster

The method of destroying a Kubernetes cluster depends on how you create it. Here are the steps for destroying a Kubernetes cluster.

<SimpleTab>
<div label="kind">

If you use kind to create the Kubernetes cluster, run the following command to destroy it:

{{< copyable "shell-regular" >}}

``` shell
kind delete cluster
```

</div>

<div label="minikube">

If you use minikube to create the Kubernetes cluster, run the following command to destroy it:

{{< copyable "shell-regular" >}}

``` shell
minikube delete
```

</div>
</SimpleTab>

## See also

If you want to do a production-grade deployment, refer to the following resources:

On public clouds:

- [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md)
- [Deploy TiDB on GCP GKE](deploy-on-gcp-gke.md)
- [Deploy TiDB on Azure AKS](deploy-on-azure-aks.md)
- [Deploy TiDB on Alibaba Cloud ACK](deploy-on-alibaba-cloud.md)

In a self-managed Kubernetes cluster:

- Familiarize yourself with [Prerequisites for TiDB in Kubernetes](prerequisites.md)
- [Configure the local PV](configure-storage-class.md#local-pv-configuration) for your Kubernetes cluster to achieve high performance for TiKV
- [Deploy TiDB Operator in Kubernetes](deploy-tidb-operator.md)
- [Deploy TiDB in General Kubernetes](deploy-on-general-kubernetes.md)