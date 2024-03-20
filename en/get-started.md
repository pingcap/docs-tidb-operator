---
title: Get Started with TiDB on Kubernetes
summary: Learn how to quickly deploy a TiDB cluster on Kubernetes using TiDB Operator.
aliases: ['/docs/tidb-in-kubernetes/dev/get-started/','/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-dind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-kind/', '/docs/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-minikube/','/docs/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind/','/docs/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube/','/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind','/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube']
---

# Get Started with TiDB on Kubernetes

This document introduces how to create a simple Kubernetes cluster and use it to deploy a basic test TiDB cluster using TiDB Operator.

> **Warning:**
>
> This document is for demonstration purposes only. **Do not** follow it in production environments. For deployment in production environments, refer to the instructions in [See also](#see-also).

To deploy TiDB Operator and a TiDB cluster, follow these steps:

1. [Create a test Kubernetes cluster](#step-1-create-a-test-kubernetes-cluster)
2. [Deploy TiDB Operator](#step-2-deploy-tidb-operator)
3. [Deploy a TiDB cluster and its monitoring services](#step-3-deploy-a-tidb-cluster-and-its-monitoring-services)
4. [Connect to a TiDB cluster](#step-4-connect-to-tidb)
5. [Upgrade a TiDB cluster](#step-5-upgrade-a-tidb-cluster)
6. [Destroy the TiDB cluster and the Kubernetes cluster](#step-6-destroy-the-tidb-cluster-and-the-kubernetes-cluster)

You can watch the following video (approximately 12 minutes) to learn how to get started with TiDB Operator.

<iframe width="600" height="450" src="https://www.youtube.com/embed/llYaXvtlqdE" title="TiDB Operator Quick Start" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Step 1: Create a test Kubernetes cluster

This section describes two methods for creating a simple Kubernetes cluster. After creating a Kubernetes cluster, you can use it to test TiDB clusters managed by TiDB Operator. Choose the method that best suits your environment.

- [Method 1: Create a Kubernetes cluster using kind](#method-1-create-a-kubernetes-cluster-using-kind): Deploy a Kubernetes cluster in Docker using kind, a common and recommended method.
- [Method 2: Create a Kubernetes cluster using minikube](#method-2-create-a-kubernetes-cluster-using-minikube): Deploy a Kubernetes cluster locally in a VM using minikube.

Alternatively, you can deploy a Kubernetes cluster on Google Kubernetes Engine on Google Cloud using the [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=en/deploy-tidb-from-kubernetes-gke.md).

### Method 1: Create a Kubernetes cluster using kind

This section explains how to deploy a Kubernetes cluster using [kind](https://kind.sigs.k8s.io/).

kind is a popular tool for running local Kubernetes clusters using Docker containers as cluster nodes. For available tags, see [Docker Hub](https://hub.docker.com/r/kindest/node/tags). The latest version of kind is used by default.

Before deployment, ensure that the following requirements are met:

- [Docker](https://docs.docker.com/install/): version >= 18.09
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/): version >= 0.8.0
- For Linux, the value of the sysctl parameter [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) should be set to `1`.

Here is an example using `kind` v0.8.1:

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

Before deployment, ensure that the following requirements are met:

- [minikube](https://minikube.sigs.k8s.io/docs/start/): version 1.0.0 or later versions. Newer versions like v1.24 are recommended. minikube requires a compatible hypervisor. For details, refer to minikube installation instructions.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): version >= 1.12

#### Start a minikube Kubernetes cluster

After installing minikube, run the following command to start a minikube Kubernetes cluster:

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

To interact with the cluster, you can use `kubectl`, which is included as a sub-command in `minikube`. To make the `kubectl` command available, you can either add the following alias definition command to your shell profile or run the following alias definition command after opening a new shell.

```
alias kubectl='minikube kubectl --'
```

Run the following command to check the status of Kubernetes and ensure that `kubectl` can connect to it:

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

## Step 2: Deploy TiDB Operator

To deploy TiDB Operator, you need to follow these steps:

### Install TiDB Operator CRDs

First, you need to install the Custom Resource Definitions (CRDs) that are required for TiDB Operator. These CRDs implement different components of the TiDB cluster.

To install the CRDs, run the following command:

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
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
> If you are using a Kubernetes version earlier than 1.16, only the v1beta1 CRD is supported. In that case, you need to change `crd.yaml` in the preceding command to `crd_v1beta1.yaml`.

### Install TiDB Operator

To install TiDB Operator, you can use [Helm 3](https://helm.sh/docs/intro/install/). Follow these steps:

1. Add the PingCAP repository:

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

    ```shell
    kubectl create namespace tidb-admin
    ```

    <details>
    <summary>Expected output</summary>

    ```
    namespace/tidb-admin created
    ```

    </details>

3. Install TiDB Operator:

    ```shell
    helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.5.2
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

Once all the Pods are in the "Running" state, you can proceed to the next step.

## Step 3: Deploy a TiDB cluster and its monitoring services

This section describes how to deploy a TiDB cluster and its monitoring services.

### Deploy a TiDB cluster

```shell
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

If you need to deploy a TiDB cluster on an ARM64 machine, refer to [Deploying a TiDB Cluster on ARM64 Machines](deploy-cluster-on-arm64.md).

> **Notes:**
>
> Starting from v8.0.0, PD supports the [microservice mode](pd-microservices.md). To deploy PD microservices, use the following command:
>
>
> ``` shell
> kubectl create namespace tidb-cluster && \
>     kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/pd-micro-service-cluster.yaml
> ```
>
> View the Pod status:
>
> ``` shell
> watch kubectl get po -n tidb-cluster
> ```
>
> ```
> NAME                              READY   STATUS    RESTARTS   AGE
> basic-discovery-6bb656bfd-xl5pb   1/1     Running   0          9m
> basic-pd-0                        1/1     Running   0          9m
> basic-scheduling-0                1/1     Running   0          9m
> basic-tidb-0                      2/2     Running   0          7m
> basic-tikv-0                      1/1     Running   0          8m
> basic-tso-0                       1/1     Running   0          9m
> basic-tso-1                       1/1     Running   0          9m
> ```

### Deploy TiDB Dashboard independently

```shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-dashboard.yaml
```

<details>
<summary>Expected output</summary>

```
tidbdashboard.pingcap.com/basic created
```

</details>

### Deploy TiDB monitoring services

```shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-monitor.yaml
```

<details>
<summary>Expected output</summary>

```
tidbmonitor.pingcap.com/basic created
```

</details>

### View the Pod status

```shell
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

Wait until all Pods for each service are started. Once you see that the Pods for each type (`-pd`, `-tikv`, and `-tidb`) are in the "Running" state, you can press <kbd>Ctrl</kbd>+<kbd>C</kbd> to return to the command line and proceed with connecting to your TiDB cluster.

## Step 4: Connect to TiDB

To connect to TiDB, you can use the MySQL client since TiDB supports the MySQL protocol and most of its syntax.

### Install the MySQL client

Before connecting to TiDB, make sure you have a MySQL-compatible client installed on the host where `kubectl` is installed. This can be the `mysql` executable from an installation of MySQL Server, MariaDB Server, Percona Server, or a standalone client executable from your operating system's package.

### Forward port 4000

To connect to TiDB, you need to forward a port from the local host to the TiDB service on Kubernetes.

First, get a list of services in the `tidb-cluster` namespace:

```shell
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

In this case, the TiDB service is called `basic-tidb`. Run the following command to forward this port from the local host to the cluster:

```shell
kubectl port-forward -n tidb-cluster svc/basic-tidb 14000:4000 > pf14000.out &
```

If port `14000` is already occupied, you can replace it with an available port. This command runs in the background and writes its output to a file named `pf14000.out`. You can continue to run the command in the current shell session.

### Connect to the TiDB service

> **Note:**
>
> To connect to TiDB (version < v4.0.7) using a MySQL 8.0 client, if the user account has a password, you must explicitly specify `--default-auth=mysql_native_password`. This is because `mysql_native_password` is [no longer the default plugin](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password).

```shell
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

After connecting to the cluster, you can run the following commands to verify that some features are available in TiDB. Note that some commands require TiDB 4.0 or higher versions. If you have deployed an earlier version, you need to [upgrade the TiDB cluster](#step-5-upgrade-a-tidb-cluster).

<details>
<summary>Create a<code>hello_world</code>table</summary>

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
         tidb_version(): Release Version: v7.5.0
                Edition: Community
        Git Commit Hash: 700beafa79844b7b48dcba1c452ea3ff49d8f271
             Git Branch: heads/refs/tags/v7.5.0
         UTC Build Time: 2023-11-10 14:38:24
              GoVersion: go1.21.3
           Race Enabled: false
Check Table Before Drop: false
                  Store: tikv
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

This command is effective only in TiDB 4.0 or later versions. If your TiDB does not support the command, you need to [upgrade the TiDB cluster](#step-5-upgrade-a-tidb-cluster).

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

To access the Grafana dashboard locally, you need to forward the port for Grafana:

```shell
kubectl port-forward -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

You can access the Grafana dashboard at <http://localhost:3000> on the host where you run `kubectl`. The default username and password in Grafana are both `admin`.

Note that if you run `kubectl` in a Docker container or on a remote host instead of your local host, you cannot access the Grafana dashboard at <http://localhost:3000> from your browser. In this case, you can run the following command to listen on all addresses:

```bash
kubectl port-forward --address 0.0.0.0 -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

Then access Grafana through <http://${remote-server-IP}:3000>.

For more information about monitoring the TiDB cluster in TiDB Operator, refer to [Deploy Monitoring and Alerts for a TiDB Cluster](monitor-a-tidb-cluster.md).

### Access the TiDB Dashboard web UI

To access the TiDB Dashboard web UI locally, you need to forward the port for TiDB Dashboard:

```shell
kubectl port-forward -n tidb-cluster svc/basic-tidb-dashboard-exposed 12333 > pf12333.out &
```

You can access the panel of TiDB Dashboard at <http://localhost:12333> on the host where you run `kubectl`.

Note that if you run `kubectl port-forward` in a Docker container or on a remote host instead of your local host, you cannot access TiDB Dashboard using `localhost` from your local browser. In this case, you can run the following command to listen on all addresses:

```bash
kubectl port-forward --address 0.0.0.0 -n tidb-cluster svc/basic-tidb-dashboard-exposed 12333 > pf12333.out &
```

Then access TiDB Dashboard through `http://${remote-server-IP}:12333`.

## Step 5: Upgrade a TiDB cluster

TiDB Operator simplifies the process of performing a rolling upgrade of a TiDB cluster. This section describes how to upgrade your TiDB cluster to the "nightly" release.

Before proceeding, it is important to familiarize yourself with the `kubectl patch` sub-command. This command lets you directly apply changes to the running cluster resources. There are different patch strategies available, each with its own capabilities, limitations, and allowed formats. For more information, refer to the [Kubernetes Patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) document.

### Modify the TiDB cluster version

To update the version of the TiDB cluster to "nightly," you can use a JSON merge patch. Execute the following command:

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

To monitor the progress of the cluster upgrade and observe the restart of its components, run the following command. You should see some Pods transitioning from `Terminating` to `ContainerCreating` and finally to `Running`.

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

Once all Pods have been restarted, you can verify that the cluster's version number has been updated.

Note that if you had previously set up port forwarding, you will need to reset it because the Pods it forwarded to have been destroyed and recreated.

```
kubectl port-forward -n tidb-cluster svc/basic-tidb 24000:4000 > pf24000.out &
```

If port `24000` is already in use, you can replace it with an available port.

### Check the TiDB cluster version

To confirm the TiDB cluster's version, execute the following command:

```
mysql --comments -h 127.0.0.1 -P 24000 -u root -e 'select tidb_version()\G'
```

<details>
<summary>Expected output</summary>

Note that `nightly` is not a fixed version and the version might vary depending on the time the command is run.

```
*************************** 1. row ***************************
tidb_version(): Release Version: v7.5.0
Edition: Community
Git Commit Hash: 700beafa79844b7b48dcba1c452ea3ff49d8f271
Git Branch: heads/refs/tags/v7.5.0
UTC Build Time: 2023-11-10 14:38:24
GoVersion: go1.21.3
Race Enabled: false
Check Table Before Drop: false
Store: tikv
```

</details>

## Step 6: Destroy the TiDB cluster and the Kubernetes cluster

After you finish testing, you can destroy the TiDB cluster and the Kubernetes cluster.

### Destroy the TiDB cluster

To destroy the TiDB cluster, follow these steps:

#### Stop `kubectl` port forwarding

If you have any running `kubectl` processes that are forwarding ports, make sure to end them by running the following command:

```shell
pgrep -lfa kubectl
```

#### Delete the TiDB cluster

To delete the TiDB cluster, use the following command:

```shell
kubectl delete tc basic -n tidb-cluster
```

In this command, `tc` is short for `tidbclusters`.

#### Delete TiDB monitoring services

To delete the TiDB monitoring services, run the following command:

```shell
kubectl delete tidbmonitor basic -n tidb-cluster
```

#### Delete PV data

If your deployment includes persistent data storage, deleting the TiDB cluster does not remove the data in the cluster. If you do not need the data, you can clean it by running the following commands:

```shell
kubectl delete pvc -n tidb-cluster -l app.kubernetes.io/instance=basic,app.kubernetes.io/managed-by=tidb-operator && \
kubectl get pv -l app.kubernetes.io/namespace=tidb-cluster,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=basic -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```

#### Delete namespaces

To ensure that there are no remaining resources, delete the namespace used for your TiDB cluster by running the following command:

```shell
kubectl delete namespace tidb-cluster
```

### Destroy the Kubernetes cluster

The method for destroying a Kubernetes cluster depends on how it was created. Here are the steps for destroying a Kubernetes cluster based on the creation method:

<SimpleTab>
<div label="kind">

If you created the Kubernetes cluster using kind, use the following command to destroy it:

```shell
kind delete cluster
```

</div>

<div label="minikube">

If you created the Kubernetes cluster using minikube, use the following command to destroy it:

```shell
minikube delete
```

</div>
</SimpleTab>

## See also

If you are interested in deploying a TiDB cluster in production environments, refer to the following documents:

On public clouds:

- [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md)
- [Deploy TiDB on Google Cloud GKE](deploy-on-gcp-gke.md)
- [Deploy TiDB on Azure AKS](deploy-on-azure-aks.md)
- [Deploy TiDB on Alibaba Cloud ACK](deploy-on-alibaba-cloud.md)

In a self-managed Kubernetes cluster:

- Familiarize yourself with the [Prerequisites for TiDB on Kubernetes](prerequisites.md)
- [Configure the local PV](configure-storage-class.md#local-pv-configuration) for your Kubernetes cluster to achieve high performance for TiKV
- [Deploy TiDB Operator on Kubernetes](deploy-tidb-operator.md)
- [Deploy TiDB on General Kubernetes](deploy-on-general-kubernetes.md)
