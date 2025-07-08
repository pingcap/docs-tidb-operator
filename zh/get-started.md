---
title: 在 Kubernetes 上快速上手 TiDB
summary: 介绍如何快速地在 Kubernetes 上使用 TiDB Operator 部署 TiDB 集群。
---

# 在 Kubernetes 上快速上手 TiDB

本文档介绍了如何创建一个简单的 Kubernetes 集群，部署 TiDB Operator，并使用 TiDB Operator 部署 TiDB 集群。

> **警告：**
>
> 本文中的部署说明仅用于测试目的，**不要**直接用于生产环境。如果要在生产环境部署，请参阅[在 Kubernetes 上部署 TiDB 集群](deploy-tidb-cluster.md)。

部署的基本步骤如下：

1. [创建 Kubernetes 测试集群](#第-1-步创建-kubernetes-测试集群)
2. [部署 TiDB Operator](#第-2-步部署-tidb-operator)
3. [部署 TiDB 集群](#第-3-步部署-tidb-集群)
4. [连接 TiDB 集群](#第-4-步连接-tidb-集群)

## 第 1 步：创建 Kubernetes 测试集群

本节介绍如何使用 [kind](https://kind.sigs.k8s.io/) 创建一个 Kubernetes 测试集群。你也可以参考 [Kubernetes 官方文档](https://kubernetes.io/docs/setup/#learning-environment)，选择其他方法部署 Kubernetes 集群。

kind 可以使用容器作为集群节点运行本地 Kubernetes 集群。请参阅 [kind 官方文档](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)完成安装。

以下以 kind 0.24.0 版本为例：

```shell
kind create cluster --name tidb-operator
```

<details>
<summary>点击查看期望输出</summary>

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

检查集群是否创建成功：

```shell
kubectl cluster-info --context kind-tidb-operator
```

<details>
<summary>点击查看期望输出</summary>

```
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

</details>

Kubernetes 集群部署完成，现在就可以开始部署 TiDB Operator 了！

## 第 2 步：部署 TiDB Operator

部署 TiDB Operator 的过程分为两步：

1. 安装 TiDB Operator CRDs
2. 安装 TiDB Operator

### 安装 TiDB Operator CRDs

TiDB Operator 包含许多实现 TiDB 集群不同组件的自定义资源类型 (CRD)。执行以下命令安装 CRD 到集群中：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.6/tidb-operator.crds.yaml --server-side
```

### 安装 TiDB Operator

执行以下命令安装 TiDB Operator 到集群中：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.6/tidb-operator.yaml --server-side
```

检查 TiDB Operator 组件是否正常运行起来：

```shell
kubectl get pods --namespace tidb-admin
```

<details>
<summary>点击查看期望输出</summary>

```
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m22s
```

</details>

当所有的 pods 都处于 Running 状态时，继续下一步。

## 第 3 步：部署 TiDB 集群

按照以下步骤部署 TiDB 集群：

1. 创建命名空间 Namespace：

    > **注意：**
    >
    > 暂不支持跨 Namespace 引用 `Cluster`。请确保所有组件部署在同一个 Kubernetes Namespace 中。

    ```shell
    kubectl create namespace db
    ```

2. 部署 TiDB 集群：

    方法一：使用以下命令创建一个包含 PD、TiKV 和 TiDB 组件的 TiDB 集群

    <SimpleTab>
    <div label="Cluster">

    创建 `Cluster`：

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

    创建 PD 组件：

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

    创建 TiKV 组件：

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

    创建 TiDB 组件：

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

    方法二：将以上 YAML 文件保存到本地目录中，并使用以下命令一次性部署 TiDB 集群

    ```shell
    kubectl apply -f ./<directory> --server-side
    ```

3. 查看 Pod 状态：

    ```shell
    watch kubectl get pods -n db
    ```

    <details>
    <summary>点击查看期望输出</summary>

    ```
    NAME               READY   STATUS    RESTARTS   AGE
    pd-pd-68t96d       1/1     Running   0          2m
    tidb-tidb-coqwpi   1/1     Running   0          2m
    tikv-tikv-sdoxy4   1/1     Running   0          2m
    ```

    </details>

    所有组件的 Pod 都启动后，每种类型组件（`pd`、`tikv` 和 `tidb`）都会处于 Running 状态。此时，你可以按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 返回命令行，然后进行下一步。

## 第 4 步：连接 TiDB 集群

由于 TiDB 支持 MySQL 传输协议及其绝大多数的语法，因此你可以直接使用 `mysql` 命令行工具连接 TiDB 进行操作。以下说明连接 TiDB 集群的步骤。

### 安装 `mysql` 命令行工具

要连接到 TiDB，你需要在使用 `kubectl` 的主机上安装与 MySQL 兼容的命令行客户端。可以安装 MySQL Server、MariaDB Server 和 Percona Server 的 MySQL 可执行文件，也可以从操作系统软件仓库中安装。

### 转发 TiDB 服务 4000 端口

本步骤将端口从本地主机转发到 Kubernetes 中的 TiDB **Service**。

首先，获取 `db` 命名空间中的服务列表：

```shell
kubectl get svc -n db
```

<details>
<summary>点击查看期望输出</summary>

```
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)               AGE
pd-pd            ClusterIP   10.96.229.12    <none>        2379/TCP,2380/TCP     3m
pd-pd-peer       ClusterIP   None            <none>        2379/TCP,2380/TCP     3m
tidb-tidb        ClusterIP   10.96.174.237   <none>        4000/TCP,10080/TCP    3m
tidb-tidb-peer   ClusterIP   None            <none>        10080/TCP             3m
tikv-tikv-peer   ClusterIP   None            <none>        20160/TCP,20180/TCP   3m
```

</details>

这个例子中，TiDB **Service** 是 **tidb-tidb**。

然后，使用以下命令转发本地端口到集群：

```shell
kubectl port-forward -n db svc/tidb-tidb 14000:4000 > pf14000.out &
```

如果端口 `14000` 已经被占用，可以更换一个空闲端口。命令会在后台运行，并将输出转发到文件 `pf14000.out`。所以，你可以继续在当前 shell 会话中执行命令。

### 连接 TiDB 服务

> **注意：**
>
> 当使用 MySQL Client 8.0 访问 TiDB 服务（TiDB 版本 < v4.0.7）时，如果用户账户有配置密码，必须显式指定 `--default-auth=mysql_native_password` 参数，因为 `mysql_native_password` [不再是默认的插件](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password)。

```shell
mysql --comments -h 127.0.0.1 -P 14000 -u root
```

<details>
<summary>点击查看期望输出</summary>

```
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 178505
Server version: 8.0.11-TiDB-v8.5.0 TiDB Server (Apache License 2.0) Community Edition, MySQL 8.0 compatible

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]>
```

</details>

以下是一些可以用来验证集群功能的命令。

<details>
<summary>创建 <code>hello_world</code> 表</summary>

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
<summary>查询 TiDB 版本号</summary>

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
