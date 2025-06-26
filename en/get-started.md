---
title: Get Started with TiDB on Kubernetes
summary: Learn how to quickly deploy a TiDB cluster on Kubernetes using TiDB Operator.
---

# Get Started with TiDB on Kubernetes

This document introduces how to create a simple Kubernetes cluster and use it to deploy a basic test TiDB cluster using TiDB Operator.

> **Warning:**
>
> This document is for demonstration purposes only. **Do not** follow it in production environments. For deployment in production environments, see [Deploy TiDB on Kubernetes](deploy-tidb-cluster.md).

To deploy TiDB Operator and a TiDB cluster, follow these steps:

1. [Create a test Kubernetes cluster](#step-1-create-a-test-kubernetes-cluster)
2. [Deploy TiDB Operator](#step-2-deploy-tidb-operator)
3. [Deploy a TiDB cluster](#step-3-deploy-a-tidb-cluster)
4. [Connect to TiDB](#step-4-connect-to-tidb)

## Step 1: Create a test Kubernetes cluster

This section describes how to create a local test Kubernetes cluster using [kind](https://kind.sigs.k8s.io/). You can also refer to the [Kubernetes official documentation](https://kubernetes.io/docs/setup/#learning-environment) for other deployment options.

kind lets you run a local Kubernetes cluster using containers as nodes. To install kind, see [Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

The following uses kind v0.24.0 as an example:

```shell
kind create cluster --name tidb-operator
```

<details>
<summary>Expected output</summary>

```
create cluster with image kindest/node:v1.31.0@sha256:53df588e04085fd41ae12de0c3fe4c72f7013bba32a20e7325357a1ac94ba865
Creating cluster "tidb-operator" ...
 ✓ Ensuring node image (kindest/node:v1.31.0) 🖼
 ✓ Preparing nodes 📦 📦 📦 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-tidb-operator"
You can now use your cluster with:

kubectl cluster-info --context kind-tidb-operator

Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂
```

</details>

Check whether the cluster is successfully created:

```shell
kubectl cluster-info --context kind-tidb-operator
```

<details>
<summary>Expected output</summary>

```
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

</details>

Now that your Kubernetes cluster is ready, you can deploy TiDB Operator.

## Step 2: Deploy TiDB Operator

To deploy TiDB Operator, perform the following steps:

1. Install TiDB Operator CRDs
2. Install TiDB Operator

### Install TiDB Operator CRDs

TiDB Operator includes multiple Custom Resource Definitions (CRDs) that implement different components of the TiDB cluster. Run the following command to install the CRDs in the cluster:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.crds.yaml --server-side
```

### Install TiDB Operator

Run the following command to install TiDB Operator into the cluster:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.yaml --server-side
```

Check whether the TiDB Operator components are running normally:

```shell
kubectl get pods --namespace tidb-admin
```

<details>
<summary>Expected output</summary>

```
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m22s
```

</details>

When all pods are in the Running state, continue to the next step.

## Step 3: Deploy a TiDB cluster

To deploy a TiDB cluster, perform the following steps:

1. Create a namespace:

    > **Note:**
    >
    > Cross-namespace `Cluster` references are not supported. Make sure that all components are deployed in the same Kubernetes namespace.

    ```shell
    kubectl create namespace db
    ```

2. Deploy the TiDB cluster.

    Method 1: use the following command to create a TiDB cluster that includes PD, TiKV, and TiDB components

    <SimpleTab>
    <div label="Cluster">

    Create the `Cluster` resource:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: basic
      namespace: db
    ```

    ```shell
    kubectl apply -f cluster.yaml --server-side
    ```

    </div>

    <div label="PD">

    Create the PD component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: PDGroup
    metadata:
      name: pd
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 1
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
          volumes:
          - name: data
            mounts:
            - type: data
            storage: 20Gi
    ```

    ```shell
    kubectl apply -f pd.yaml --server-side
    ```

    </div>

    <div label="TiKV">

    Create the TiKV component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 1
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
          volumes:
          - name: data
            mounts:
            - type: data
            storage: 100Gi
    ```

    ```shell
    kubectl apply -f tikv.yaml --server-side
    ```

    </div>

    <div label="TiDB">

    Create the TiDB component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiDBGroup
    metadata:
      name: tidb
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 1
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
    ```

    ```shell
    kubectl apply -f tidb.yaml --server-side
    ```

    </div>
    </SimpleTab>

    Method 2: save the preceding YAML files to a local directory and deploy the TiDB cluster with a single command:

    ```shell
    kubectl apply -f ./<directory> --server-side
    ```

3. Monitor the status of Pod:

    ```shell
    watch kubectl get pods -n db
    ```

    <details>
    <summary>Expected output</summary>

    ```
    NAME               READY   STATUS    RESTARTS   AGE
    pd-pd-68t96d       1/1     Running   0          2m
    tidb-tidb-coqwpi   1/1     Running   0          2m
    tikv-tikv-sdoxy4   1/1     Running   0          2m
    ```

    </details>

    After all component Pods start, each component type (`pd`, `tikv`, and `tidb`) will be in the Running state. You can press <kbd>Ctrl</kbd>+<kbd>C</kbd> to return to the command line and proceed to the next step.

## Step 4: Connect to TiDB

Because TiDB supports the MySQL transport protocol and most of its syntax, you can use the `mysql` command-line tool to connect to TiDB directly. The following steps describe how to connect to the TiDB cluster.

### Install the `mysql` command-line tool

To connect to TiDB, you need to install a MySQL-compatible command-line client on the machine where you are running `kubectl`. You can install MySQL Server, MariaDB Server, or Percona Server MySQL executables, or install them from your operating system's software repository.

### Forward port 4000

To connect to TiDB, you need to forward a port from the local host to the TiDB service on Kubernetes.

First, list services in the `db` namespace:

```shell
kubectl get svc -n db
```

<details>
<summary>Expected output</summary>

```
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)               AGE
pd-pd            ClusterIP   10.96.229.12    <none>        2379/TCP,2380/TCP     3m
pd-pd-peer       ClusterIP   None            <none>        2379/TCP,2380/TCP     3m
tidb-tidb        ClusterIP   10.96.174.237   <none>        4000/TCP,10080/TCP    3m
tidb-tidb-peer   ClusterIP   None            <none>        10080/TCP             3m
tikv-tikv-peer   ClusterIP   None            <none>        20160/TCP,20180/TCP   3m
```

</details>

In this example, the TiDB service is `tidb-tidb`.

Then, use the following command to forward a local port to the cluster:

```shell
kubectl port-forward -n db svc/tidb-tidb 14000:4000 > pf14000.out &
```

If port `14000` is already in use, you can use a different available port. The command runs in the background and forwards output to the file `pf14000.out`, so you can continue to run commands in the current shell session.

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
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 178505
Server version: 8.0.11-TiDB-v8.5.0 TiDB Server (Apache License 2.0) Community Edition, MySQL 8.0 compatible

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]>
```

</details>

Use the following sample commands to verify the cluster is working.

<details>
<summary>Create a <code>hello_world</code> table</summary>

```sql
mysql> use test;
mysql> create table hello_world (id int unsigned not null auto_increment primary key, v varchar(32));
Query OK, 0 rows affected (0.17 sec)

mysql> select * from information_schema.tikv_region_status where db_name=database() and table_name='hello_world'\G
*************************** 1. row ***************************
                REGION_ID: 18
                START_KEY: 7480000000000000FF6800000000000000F8
                  END_KEY: 748000FFFFFFFFFFFFF900000000000000F8
                 TABLE_ID: 104
                  DB_NAME: test
               TABLE_NAME: hello_world
                 IS_INDEX: 0
                 INDEX_ID: NULL
               INDEX_NAME: NULL
             IS_PARTITION: 0
             PARTITION_ID: NULL
           PARTITION_NAME: NULL
           EPOCH_CONF_VER: 5
            EPOCH_VERSION: 57
            WRITTEN_BYTES: 0
               READ_BYTES: 0
         APPROXIMATE_SIZE: 1
         APPROXIMATE_KEYS: 0
  REPLICATIONSTATUS_STATE: NULL
REPLICATIONSTATUS_STATEID: NULL
1 row in set (0.015 sec)
```

</details>

<details>
<summary>Query the TiDB version</summary>

```sql
mysql> select tidb_version()\G
*************************** 1. row ***************************
tidb_version(): Release Version: v8.1.0
Edition: Community
Git Commit Hash: 945d07c5d5c7a1ae212f6013adfb187f2de24b23
Git Branch: HEAD
UTC Build Time: 2024-05-21 03:51:57
GoVersion: go1.21.10
Race Enabled: false
Check Table Before Drop: false
Store: tikv
1 row in set (0.001 sec)
```

</details>
