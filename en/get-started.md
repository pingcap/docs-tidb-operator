---
title: Get Started With TiDB Operator in Kubernetes
summary: Learn how to quickly deploy a TiDB cluster in Kubernetes using TiDB Operator.
aliases: ['/tidb-in-kubernetes/v1.0/deploy-tidb-from-kubernetes-kind','/docs/tidb-in-kubernetes/v1.0/deploy-tidb-from-kubernetes-kind/','/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-dind/','/docs/dev/tidb-in-kubernetes/get-started/deploy-tidb-from-kubernetes-kind/','/docs/v3.1/tidb-in-kubernetes/get-started/deploy-tidb-from-kubernetes-kind/','/docs/v3.0/tidb-in-kubernetes/get-started/deploy-tidb-from-kubernetes-kind/']
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

You can watch the following video (about 12 minutes) to learn how to get started with TiDB Operator.

<iframe width="600" height="450" src="https://www.youtube.com/embed/llYaXvtlqdE" title="TiDB Operator Quick Start" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Step 1. Create a test Kubernetes cluster

This section describes two ways to create a simple Kubernetes cluster. After creating a Kubernetes cluster, you can use it to test TiDB clusters managed by TiDB Operator. Choose whichever best matches your environment.

- [Use kind](#method-1-create-a-kubernetes-cluster-using-kind) to deploy a Kubernetes cluster in Docker. It is a common and recommended way.
- [Use minikube](#method-2-create-a-kubernetes-cluster-using-minikube) to deploy a Kubernetes cluster running locally in a VM.

Alternatively, you can deploy a Kubernetes cluster in Google Kubernetes Engine in Google Cloud Platform using the [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=en/deploy-tidb-from-kubernetes-gke.md).

### Method 1: Create a Kubernetes cluster using kind

This section shows how to deploy a Kubernetes cluster using [kind](https://kind.sigs.k8s.io/).

kind is a popular tool for running local Kubernetes clusters using Docker containers as cluster nodes. For available tags, see [Docker Hub](https://hub.docker.com/r/kindest/node/tags). The latest version of kind is used by default.

Before deployment, make sure the following requirements are satisfied:

- [Docker](https://docs.docker.com/install/): version >= 18.09
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/): version >= 0.8.0
- For Linux, the value of the sysctl parameter [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) should be set to `1`.

The following is an example of using `kind` v0.8.1:

{{< copyable "shell-regular" >}}

```shell
kind create cluster
```

<details>
<summary>Expected output</summary>

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

</details>

Check whether the cluster is successfully created:

{{< copyable "shell-regular" >}}

```shell
kubectl cluster-info
```

<details>
<summary>Expected output</summary>

```
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

</details>

You are now ready to deploy TiDB Operator.

### Method 2: Create a Kubernetes cluster using minikube

You can create a Kubernetes cluster in a VM using [minikube](https://minikube.sigs.k8s.io/docs/start/), which supports macOS, Linux, and Windows.

Before deployment, make sure the following requirements are satisfied:

- [minikube](https://minikube.sigs.k8s.io/docs/start/): version 1.0.0 or later versions. Newer versions like v1.24 is recommended. minikube requires a compatible hypervisor. For details, refer to minikube installation instructions.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12

#### Start a minikube Kubernetes cluster

After minikube is installed, run the following command to start a minikube Kubernetes cluster:

{{< copyable "shell-regular" >}}

```shell
minikube start
```

<details>
<summary>Expected output</summary>
You should see output like this, with some differences depending on your OS and hypervisor:

```
😄  minikube v1.24.0 on Darwin 12.1
✨  Automatically selected the docker driver. Other choices: hyperkit, virtualbox, ssh
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
💾  Downloading Kubernetes v1.22.3 preload ...
    > gcr.io/k8s-minikube/kicbase: 355.78 MiB / 355.78 MiB  100.00% 4.46 MiB p/
    > preloaded-images-k8s-v13-v1...: 501.73 MiB / 501.73 MiB  100.00% 5.18 MiB
🔥  Creating docker container (CPUs=2, Memory=1985MB) ...
🐳  Preparing Kubernetes v1.22.3 on Docker 20.10.8 ...
    ▪ Generating certificates and keys ...
    ▪ Booting up control plane ...
    ▪ Configuring RBAC rules ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

</details>

#### Use `kubectl` to interact with the cluster

To interact with the cluster, you can use `kubectl`, which is included as a sub-command in `minikube`. To make the `kubectl` command available, you can either add the following alias definition command to your shell profile, or run the following alias definition command after opening a new shell.

{{< copyable "shell-regular" >}}

```
alias kubectl='minikube kubectl --'
```

Run the following command to check the status of Kubernetes and ensure that `kubectl` can connect to it:

{{< copyable "shell-regular" >}}

```
kubectl cluster-info
```

<details>
<summary>Expected output</summary>

```
Kubernetes master is running at https://192.168.64.2:8443
KubeDNS is running at https://192.168.64.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

</details>

You are now ready to deploy TiDB Operator.

## Step 2. Deploy TiDB Operator

You need to install TiDB Operator CRDs first, and then install TiDB Operator.

### Install TiDB Operator CRDs

TiDB Operator includes a number of Custom Resource Definitions (CRDs) that implement different components of the TiDB cluster.

Run the following command to install the CRDs into your cluster:

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.3.8/manifests/crd.yaml
```

<details>
<summary>Expected output</summary>

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
> For Kubernetes earlier than 1.16, only v1beta1 CRD is supported. Therefore, you need to change `crd.yaml` in the preceding command to `crd_v1beta1.yaml`.

### Install TiDB Operator

This section describes how to install TiDB Operator using [Helm 3](https://helm.sh/docs/intro/install/).

1. Add the PingCAP repository:

    {{< copyable "shell-regular" >}}

    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

    <details>
    <summary>Expected output</summary>

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
    <summary>Expected output</summary>

    ```
    namespace/tidb-admin created
    ```

    </details>

3. Install TiDB Operator

    {{< copyable "shell-regular" >}}

    ```shell
    helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.3.8
    ```

    <details>
    <summary>Expected output</summary>

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
<summary>Expected output</summary>

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
<summary>Expected output</summary>

```
namespace/tidb-cluster created
tidbcluster.pingcap.com/basic created
```

</details>

If you need to deploy a TiDB cluster on an ARM64 machine, refer to [Deploy a TiDB Cluster on ARM64 Machines](deploy-cluster-on-arm64.md).

### Deploy TiDB monitoring services

{{< copyable "shell-regular" >}}

``` shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-monitor.yaml
```

<details>
<summary>Expected output</summary>

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
<summary>Expected output</summary>

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
<summary>Expected output</summary>

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
kubectl port-forward -n tidb-cluster svc/basic-tidb 14000:4000 > pf14000.out &
```

If the port `14000` is already occupied, you can replace it with an available port. This command runs in the background and writes its output to a file named `pf14000.out`. You can continue to run the command in the current shell session.

### Connect to the TiDB service

> **Note:**
>
> To connect to TiDB (< v4.0.7) using a MySQL 8.0 client, if the user account has a password, you must explicitly specify `--default-auth=mysql_native_password`. This is because `mysql_native_password` is [no longer the default plugin](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password).

{{< copyable "shell-regular" >}}

``` shell
mysql --comments -h 127.0.0.1 -P 14000 -u root
```

<details>
<summary>Expected output</summary>

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

After connecting to the cluster, you can run the following commands to verify that some features available in TiDB. Note that some commands require TiDB 4.0 or higher versions. If you have deployed an earlier version, you need to [upgrade the TiDB cluster](#step-5-upgrade-a-tidb-cluster).

<details>
<summary>Create a <code>hello_world</code> table</summary>

```sql
mysql> use test;
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
<summary>Query the TiDB version</summary>

```sql
mysql> select tidb_version()\G
*************************** 1. row ***************************
  tidb_version(): Release Version: v6.1.0
         Edition: Community
 Git Commit Hash: 4a1b2e9fe5b5afb1068c56de47adb07098d768d6
      Git Branch: heads/refs/tags/v6.1.0
  UTC Build Time: 2021-11-24 13:32:39
       GoVersion: go1.16.4
    Race Enabled: false
TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
Check Table Before Drop: false
1 row in set (0.01 sec)
```

</details>

<details>
<summary>Query the TiKV store status</summary>

```sql
mysql> select * from information_schema.tikv_store_status\G
*************************** 1. row ***************************
            STORE_ID: 4
             ADDRESS: basic-tikv-0.basic-tikv-peer.tidb-cluster.svc:20160
         STORE_STATE: 0
    STORE_STATE_NAME: Up
               LABEL: null
             VERSION: 5.2.1
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
<summary>Query the TiDB cluster information</summary>

This command is effective only in TiDB 4.0 or later versions. If your TiDB does not support the command, you need to [Upgrade a TiDB cluster](#step-5-upgrade-a-tidb-cluster).

```sql
mysql> select * from information_schema.cluster_info\G
*************************** 1. row ***************************
            TYPE: tidb
        INSTANCE: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:4000
  STATUS_ADDRESS: basic-tidb-0.basic-tidb-peer.tidb-cluster.svc:10080
         VERSION: 5.2.1
        GIT_HASH: 689a6b6439ae7835947fcaccf329a3fc303986cb
      START_TIME: 2020-05-28T22:50:11Z
          UPTIME: 3m21.459090928s
*************************** 2. row ***************************
            TYPE: pd
        INSTANCE: basic-pd:2379
  STATUS_ADDRESS: basic-pd:2379
         VERSION: 5.2.1
        GIT_HASH: 56d4c3d2237f5bf6fb11a794731ed1d95c8020c2
      START_TIME: 2020-05-28T22:45:04Z
          UPTIME: 8m28.459091915s
*************************** 3. row ***************************
            TYPE: tikv
        INSTANCE: basic-tikv-0.basic-tikv-peer.tidb-cluster.svc:20160
  STATUS_ADDRESS: 0.0.0.0:20180
         VERSION: 5.2.1
        GIT_HASH: 198a2cea01734ce8f46d55a29708f123f9133944
      START_TIME: 2020-05-28T22:48:21Z
          UPTIME: 5m11.459102648s
3 rows in set (0.01 sec)
```

</details>

### Access the Grafana dashboard

You can forward the port for Grafana to access the Grafana dashboard locally:

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

You can access the Grafana dashboard at <http://localhost:3000> on the host where you run `kubectl`. The default username and password in Grafana are both `admin`.

Note that if you run `kubectl` in a Docker container or on a remote host instead of your local host, you can not access the Grafana dashboard at <http://localhost:3000> from your browser. In this case, you can run the following command to listen on all addresses.

```bash
kubectl port-forward --address 0.0.0.0 -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

Then access Grafana through <http://${remote-server-IP}:3000>.

For more information about monitoring the TiDB cluster in TiDB Operator, refer to [Deploy Monitoring and Alerts for a TiDB Cluster](monitor-a-tidb-cluster.md).

## Step 5. Upgrade a TiDB cluster

TiDB Operator also makes it easy to perform a rolling upgrade of the TiDB cluster. This section describes how to upgrade your TiDB cluster to the "nightly" release.

Before that, you need to get familiar with a `kubectl` sub-command `kubectl patch`. It applies a specification change directly to the running cluster resources. There are several different patch strategies, each of which has various capabilities, limitations, and allowed formats. For details, see [Kubernetes Patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/)

### Modify the TiDB cluster version

In this case, you can use a JSON merge patch to update the version of the TiDB cluster to "nightly":

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc basic -n tidb-cluster --type merge -p '{"spec": {"version": "nightly"} }'
```

<details>
<summary>Expected output</summary>

```
tidbcluster.pingcap.com/basic patched
```

</details>

### Wait for Pods to restart

To follow the progress of the cluster as its components are upgraded, run the following command. You should see some Pods transiting to `Terminating` and then back to `ContainerCreating` and then to `Running`.

{{< copyable "shell-regular" >}}

```
watch kubectl get po -n tidb-cluster
```

<details>
<summary>Expected output</summary>

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

Note that you need to reset any port forwarding you set up in a previous step, because the pods they forwarded to have been destroyed and recreated.

{{< copyable "shell-regular" >}}

```
kubectl port-forward -n tidb-cluster svc/basic-tidb 24000:4000 > pf24000.out &
```

If the port `24000` is already occupied, you can replace it with an available port.

### Check the TiDB cluster version

{{< copyable "shell-regular" >}}

```
mysql --comments -h 127.0.0.1 -P 24000 -u root -e 'select tidb_version()\G'
```

<details>
<summary>Expected output</summary>

Note that `nightly` is not a fixed version. Running the command above at a different time might return different results.

```
*************************** 1. row ***************************
tidb_version(): Release Version: v6.1.0-alpha-445-g778e188fa
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

This section introduces how to destroy a TiDB cluster.

#### Stop `kubectl` port forwarding

If you still have running `kubectl` processes that are forwarding ports, end them:

{{< copyable "shell-regular" >}}

```shell
pgrep -lfa kubectl
```

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

If your deployment has persistent data storage, deleting the TiDB cluster does not remove the data in the cluster. If you do not need the data, run the following commands to clean it:

{{< copyable "shell-regular" >}}

```shell
kubectl delete pvc -n tidb-cluster -l app.kubernetes.io/instance=basic,app.kubernetes.io/managed-by=tidb-operator && \
kubectl get pv -l app.kubernetes.io/namespace=tidb-cluster,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=basic -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```

#### Delete namespaces

To ensure that there are no lingering resources, delete the namespace used for your TiDB cluster.

{{< copyable "shell-regular" >}}

```shell
kubectl delete namespace tidb-cluster
```

### Destroy the Kubernetes cluster

The method of destroying a Kubernetes cluster depends on how you create it. Here are the steps for destroying a Kubernetes cluster.

<SimpleTab>
<div label="kind">

To destroy a Kubernetes cluster created using kind, run the following command:

{{< copyable "shell-regular" >}}

``` shell
kind delete cluster
```

</div>

<div label="minikube">

To destroy a Kubernetes cluster created using minikube, run the following command:

{{< copyable "shell-regular" >}}

``` shell
minikube delete
```

</div>
</SimpleTab>

## See also

If you want to deploy a TiDB cluster in production environments, refer to the following documents:

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