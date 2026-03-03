---
title: 在 Kubernetes 上快速上手 TiDB
summary: 介绍如何快速地在 Kubernetes 上使用 TiDB Operator 部署 TiDB 集群
---

# 在 Kubernetes 上快速上手 TiDB

本文档介绍了如何创建一个简单的 Kubernetes 集群，部署 TiDB Operator，并使用 TiDB Operator 部署 TiDB 集群。

> **警告：**
>
> 本文中的部署说明仅用于测试目的，**不要**直接用于生产环境。如果要在生产环境部署，请参阅[探索更多](#探索更多)。

部署的基本步骤如下：

1. [创建 Kubernetes 测试集群](#第-1-步创建-kubernetes-测试集群)
2. [部署 TiDB Operator](#第-2-步部署-tidb-operator)
3. [部署 TiDB 集群和监控](#第-3-步部署-tidb-集群和监控)
4. [连接 TiDB 集群](#第-4-步连接-tidb-集群)
5. [升级 TiDB 集群](#第-5-步升级-tidb-集群)
6. [销毁 TiDB 集群和 Kubernetes 集群](#第-6-步销毁-tidb-集群和-kubernetes-集群)

你可以先观看下面视频（时长约 12 分钟）。该视频完整的演示了快速上手的操作流程。

<video src="https://tidb-docs.s3.us-east-2.amazonaws.com/Operator+quick+start+(11+mins).mp4" width="600px" height="450px" controls="controls" poster="https://tidb-docs.s3.us-east-2.amazonaws.com/thumbnail+-+TiDB+operator.png"></video>

## 第 1 步：创建 Kubernetes 测试集群

本节介绍了两种创建 Kubernetes 测试集群的方法，可用于测试 TiDB Operator 管理的 TiDB 集群。

- [使用 kind](#方法一使用-kind-创建-kubernetes-集群) 创建在 Docker 中运行的 Kubernetes，这是目前比较通用的部署方式。
- [使用 minikube](#方法二使用-minikube-创建-kubernetes-集群) 创建在虚拟机中运行的 Kubernetes

你也可以使用 [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=zh/deploy-tidb-from-kubernetes-gke.md) 在 Google Cloud Platform 的 Google Kubernetes Engine 中部署 Kubernetes 集群。

### 方法一：使用 kind 创建 Kubernetes 集群

目前比较通用的方式是使用 [kind](https://kind.sigs.k8s.io/) 部署本地测试 Kubernetes 集群。kind 适用于使用 Docker 容器作为集群节点运行本地 Kubernetes 集群。请参阅 [Docker Hub](https://hub.docker.com/r/kindest/node/tags) 以查看可用 tags。默认使用当前 kind 支持的最新版本。

部署前，请确保满足以下要求：

- [docker](https://docs.docker.com/install/)：版本 >= 18.09
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)：版本 >= 1.12
- [kind](https://kind.sigs.k8s.io/)：版本 >= 0.8.0
- 若使用 Linux, [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) 需要被设置为 `1`

以下以 0.8.1 版本为例：

{{< copyable "shell-regular" >}}

```shell
kind create cluster
```

<details>
<summary>点击查看期望输出</summary>

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

检查集群是否创建成功：

{{< copyable "shell-regular" >}}

```shell
kubectl cluster-info
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

### 方法二：使用 minikube 创建 Kubernetes 集群

[minikube](https://minikube.sigs.k8s.io/docs/start/) 可以在虚拟机中创建一个 Kubernetes 集群。minikube 可在 macOS, Linux 和 Windows 上运行。

部署前，请确保满足以下要求：

- [minikube](https://minikube.sigs.k8s.io/docs/start/)：版本 1.0.0 及以上，推荐使用较新版本。minikube 需要安装一个兼容的 hypervisor，详情见官方安装教程。
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): 版本 >= 1.12

你可以使用 minikube start 直接启动 Kubernetes 集群，中国大陆用户也可以通过 gcr.io mirror 仓库启动 Kubernetes 集群。以下分别对这几种方法进行介绍。

#### 使用 minikube start 启动 Kubernetes 集群

安装完 minikube 后，可以执行下面命令启动 Kubernetes 集群：

{{< copyable "shell-regular" >}}

```shell
minikube start
```

<details>
<summary>点击查看期望输出</summary>
如果一切运行正常，会看到类似下面的输出，根据操作系统和使用的 hypervisor 会有些许差异。

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

#### 使用 gcr.io mirror 仓库启动 Kubernetes 集群

中国大陆用户可以使用国内 gcr.io mirror 仓库，例如 `registry.cn-hangzhou.aliyuncs.com/google_containers`。

{{< copyable "shell-regular" >}}

``` shell
minikube start --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers
```

#### 使用 `kubectl` 进行集群操作

你可以使用 `minikube` 的子命令 `kubectl` 来进行集群操作。要使 `kubectl` 命令生效，你需要在 shell 配置文件中添加以下别名设置命令，或者在打开一个新的 shell 后执行以下别名设置命令。

{{< copyable "shell-regular" >}}

```
alias kubectl='minikube kubectl --'
```

执行以下命令检查集群状态，并确保可以通过 `kubectl` 访问集群:

{{< copyable "shell-regular" >}}

```
kubectl cluster-info
```

<details>
<summary>点击查看期望输出</summary>

```
Kubernetes master is running at https://192.168.64.2:8443
KubeDNS is running at https://192.168.64.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

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

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/manifests/crd.yaml
```

<details>
<summary>点击查看期望输出</summary>

```
customresourcedefinition.apiextensions.k8s.io/tidbclusters.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/backups.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/restores.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/backupschedules.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/tidbmonitors.pingcap.com created
customresourcedefinition.apiextensions.k8s.io/tidbinitializers.pingcap.com created
```

</details>

> **注意：**
>
> 对于 Kubernetes 1.16 之前的版本，Kubernetes 仅支持 v1beta1 版本的 CRD，你需要将上述命令中的 `crd.yaml` 修改为 `crd_v1beta1.yaml`。

### 安装 TiDB Operator

安装 [Helm 3](https://helm.sh/docs/intro/install/) 并使用 Helm 3 部署 TiDB Operator。

1. 添加 PingCAP 仓库。

    {{< copyable "shell-regular" >}}

    ```shell
    helm repo add pingcap https://charts.pingcap.com/
    ```

    <details>
    <summary>点击查看期望输出</summary>

    ```
    "pingcap" has been added to your repositories
    ```

    </details>

2. 为 TiDB Operator 创建一个命名空间。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace tidb-admin
    ```

    <details>
    <summary>点击查看期望输出</summary>

    ```
    namespace/tidb-admin created
    ```

    </details>

3. 安装 TiDB Operator。

    {{< copyable "shell-regular" >}}

    ```shell
    helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.4.7
    ```

    如果访问 Docker Hub 网速较慢，可以使用阿里云上的镜像：

    {{< copyable "shell-regular" >}}

    ```
    helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.4.7 \
        --set operatorImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-operator:v1.4.7 \
        --set tidbBackupManagerImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-backup-manager:v1.4.7 \
        --set scheduler.kubeSchedulerImageName=registry.cn-hangzhou.aliyuncs.com/google_containers/kube-scheduler
    ```

    <details>
    <summary>点击查看期望输出</summary>

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

检查 TiDB Operator 组件是否正常运行起来：

{{< copyable "shell-regular" >}}

```shell
kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
```

<details>
<summary>点击查看期望输出</summary>

```
NAME                                       READY   STATUS    RESTARTS   AGE
tidb-controller-manager-6d8d5c6d64-b8lv4   1/1     Running   0          2m22s
tidb-scheduler-644d59b46f-4f6sb            2/2     Running   0          2m22s
```

</details>

当所有的 pods 都处于 Running 状态时，继续下一步。

## 第 3 步：部署 TiDB 集群和监控

下面分别介绍 TiDB 集群和监控的部署方法。

### 部署 TiDB 集群

{{< copyable "shell-regular" >}}

``` shell
kubectl create namespace tidb-cluster && \
    kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic/tidb-cluster.yaml
```

如果访问 Docker Hub 网速较慢，可以使用 UCloud 上的镜像：

{{< copyable "shell-regular" >}}

```
kubectl create namespace tidb-cluster && \
    kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic-cn/tidb-cluster.yaml
```

<details>
<summary>点击查看期望输出</summary>

```
namespace/tidb-cluster created
tidbcluster.pingcap.com/basic created
```

</details>

如果要将 TiDB 集群部署到 ARM64 机器上，可以参考[在 ARM64 机器上部署 TiDB 集群](deploy-cluster-on-arm64.md)。

### 部署独立的 TiDB Dashboard

{{< copyable "shell-regular" >}}

``` shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic/tidb-dashboard.yaml
```

如果访问 Docker Hub 网速较慢，可以使用 UCloud 上的镜像：

{{< copyable "shell-regular" >}}

```
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic-cn/tidb-dashboard.yaml
```

<details>
<summary>点击查看期望输出</summary>

```
tidbdashboard.pingcap.com/basic created
```

</details>

### 部署 TiDB 集群监控

{{< copyable "shell-regular" >}}

``` shell
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic/tidb-monitor.yaml
```

如果访问 Docker Hub 网速较慢，可以使用 UCloud 上的镜像：

{{< copyable "shell-regular" >}}

```
kubectl -n tidb-cluster apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.4.7/examples/basic-cn/tidb-monitor.yaml
```

<details>
<summary>点击查看期望输出</summary>

```
tidbmonitor.pingcap.com/basic created
```

</details>

### 查看 Pod 状态

{{< copyable "shell-regular" >}}

``` shell
watch kubectl get po -n tidb-cluster
```

<details>
<summary>点击查看期望输出</summary>

```
NAME                              READY   STATUS    RESTARTS   AGE
basic-discovery-6bb656bfd-xl5pb   1/1     Running   0          9m9s
basic-monitor-5fc8589c89-gvgjj    3/3     Running   0          8m58s
basic-pd-0                        1/1     Running   0          9m8s
basic-tidb-0                      2/2     Running   0          7m14s
basic-tikv-0                      1/1     Running   0          8m13s
```

</details>

所有组件的 Pod 都启动后，每种类型组件（`pd`、`tikv` 和 `tidb`）都会处于 Running 状态。此时，你可以按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 返回命令行，然后进行下一步。

## 第 4 步：连接 TiDB 集群

由于 TiDB 支持 MySQL 传输协议及其绝大多数的语法，因此你可以直接使用 `mysql` 命令行工具连接 TiDB 进行操作。以下说明连接 TiDB 集群的步骤。

### 安装 `mysql` 命令行工具

要连接到 TiDB，你需要在使用 `kubectl` 的主机上安装与 MySQL 兼容的命令行客户端。可以安装 MySQL Server、MariaDB Server 和 Percona Server 的 MySQL 可执行文件，也可以从操作系统软件仓库中安装。

### 转发 TiDB 服务 4000 端口

本步骤将端口从本地主机转发到 Kubernetes 中的 TiDB **Servcie**。

首先，获取 tidb-cluster 命名空间中的服务列表：

{{< copyable "shell-regular" >}}

``` shell
kubectl get svc -n tidb-cluster
```

<details>
<summary>点击查看期望输出</summary>

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

这个例子中，TiDB **Service** 是 **basic-tidb**。

然后，使用以下命令转发本地端口到集群：

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-tidb 14000:4000 > pf14000.out &
```

如果端口 `14000` 已经被占用，可以更换一个空闲端口。命令会在后台运行，并将输出转发到文件 `pf14000.out`。所以，你可以继续在当前 shell 会话中执行命令。

### 连接 TiDB 服务

> **注意：**
>
> 当使用 MySQL Client 8.0 访问 TiDB 服务（TiDB 版本 < v4.0.7）时，如果用户账户有配置密码，必须显式指定 `--default-auth=mysql_native_password` 参数，因为 `mysql_native_password` [不再是默认的插件](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password)。

{{< copyable "shell-regular" >}}

``` shell
mysql --comments -h 127.0.0.1 -P 14000 -u root
```

<details>
<summary>点击查看期望输出</summary>

```
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 178505
Server version: 5.7.25-TiDB-v7.5.0 TiDB Server (Apache License 2.0) Community Edition, MySQL 5.7 compatible

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
<summary>查询 TiDB 版本号</summary>

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
<summary>查询 TiKV 存储状态</summary>

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
<summary>查询 TiDB 集群基本信息</summary>

该命令需要 TiDB 4.0 或以上版本，如果你部署的 TiDB 版本不支持该命令，请先[升级 TiDB 集群](#第-5-步升级-tidb-集群)。

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

### 访问 Grafana 面板

你可以转发 Grafana 服务端口，以便本地访问 Grafana 面板。

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

Grafana 面板可在 kubectl 所运行的主机上通过 <http://localhost:3000> 访问。默认用户名和密码都是 "admin" 。

请注意，如果你是非本机（比如 Docker 容器或远程服务器）上运行 `kubectl port-forward`，将无法在本地浏览器里通过 `localhost:3000` 访问，可以通过下面命令监听所有地址：

```bash
kubectl port-forward --address 0.0.0.0 -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
```

然后通过 `http://${远程服务器IP}:3000` 访问 Grafana。

了解更多使用 TiDB Operator 部署 TiDB 集群监控的信息，可以查阅 [TiDB 集群监控与告警](monitor-a-tidb-cluster.md)。

### 访问 TiDB Dashboard Web UI

你可以转发 TiDB Dashboard 服务端口，以便本地访问 TiDB Dashboard 界面。

{{< copyable "shell-regular" >}}

``` shell
kubectl port-forward -n tidb-cluster svc/basic-tidb-dashboard-exposed 12333 > pf12333.out &
```

TiDB Dashboard 面板可在 kubectl 所运行的主机上通过 <http://localhost:12333> 访问。

请注意，如果你是非本机（比如 Docker 容器或远程服务器）上运行 `kubectl port-forward`，将无法在本地浏览器里通过 `localhost` 访问，可以通过下面命令监听所有地址：

```bash
kubectl port-forward --address 0.0.0.0 -n tidb-cluster svc/basic-tidb-dashboard-exposed 12333 > pf12333.out &
```

然后通过 `http://${远程服务器IP}:12333` 访问 TiDB Dashboard。

## 第 5 步：升级 TiDB 集群

TiDB Operator 还可简化 TiDB 集群的滚动升级。以下展示使用 kubectl 命令行工具更新 TiDB 版本到 nightly 版本的过程。在此之前，先了解一下 kubectl 的子命令 `kubectl patch`。 它可以直接应用补丁。Kubernetes 支持几种不同的补丁策略，每种策略有不同的功能、格式等。可参考 [Kubernetes Patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) 了解更多细节。

### 修改 TiDB 集群版本

执行以下命令，将 TiDB 集群升级到 nightly 版本：

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc basic -n tidb-cluster --type merge -p '{"spec": {"version": "nightly"} }'
```

<details>
<summary>点击查看期望输出</summary>

```
tidbcluster.pingcap.com/basic patched
```

</details>

### 等待 Pods 重启

执行以下命令以了解集群升级组件时的进度。你可以看到某些 Pods 进入 `Terminating` 状态后，又回到 `ContainerCreating`，最后重新进入 `Running` 状态。

{{< copyable "shell-regular" >}}

```
watch kubectl get po -n tidb-cluster
```

<details>
<summary>点击查看期望输出</summary>

```
NAME                              READY   STATUS        RESTARTS   AGE
basic-discovery-6bb656bfd-7lbhx   1/1     Running       0          24m
basic-pd-0                        1/1     Terminating   0          5m31s
basic-tidb-0                      2/2     Running       0          2m19s
basic-tikv-0                      1/1     Running       0          4m13s
```

</details>

### 转发 TiDB 服务端口

当所有 Pods 都重启后，将看到版本号已更改。需要注意的是，由于相关 Pods 已被销毁重建，这里需要重新设置端口转发。

{{< copyable "shell-regular" >}}

```
kubectl port-forward -n tidb-cluster svc/basic-tidb 24000:4000 > pf24000.out &
```

如果端口 `24000` 已经被占用，可以更换一个空闲端口。

### 检查 TiDB 集群版本

{{< copyable "shell-regular" >}}

```
mysql --comments -h 127.0.0.1 -P 24000 -u root -e 'select tidb_version()\G'
```

<details>
<summary>点击查看期望输出</summary>

注意， `nightly` 不是固定版本，不同时间会有不同结果。下面示例仅供参考。

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

## 第 6 步：销毁 TiDB 集群和 Kubernetes 集群

完成测试后，你可能希望销毁 TiDB 集群和 Kubernetes 集群。

### 停止 `kubectl` 的端口转发

如果你仍在运行正在转发端口的 `kubectl` 进程，请终止它们：

{{< copyable "shell-regular" >}}

```shell
pgrep -lfa kubectl
```

### 销毁 TiDB 集群

销毁 TiDB 集群的步骤如下。

#### 删除 TiDB Cluster

{{< copyable "shell-regular" >}}

```shell
kubectl delete tc basic -n tidb-cluster
```

此命令中，`tc` 为 tidbclusters 的简称。

#### 删除 TiDB Monitor

{{< copyable "shell-regular" >}}

```shell
kubectl delete tidbmonitor basic -n tidb-cluster
```

#### 删除 PV 数据

如果你的部署使用持久性数据存储，则删除 TiDB 集群将不会删除集群的数据。如果不再需要数据，可以运行以下命令来清理数据：

{{< copyable "shell-regular" >}}

```shell
kubectl delete pvc -n tidb-cluster -l app.kubernetes.io/instance=basic,app.kubernetes.io/managed-by=tidb-operator && \
kubectl get pv -l app.kubernetes.io/namespace=tidb-cluster,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=basic -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```

#### 删除命名空间

为确保没有残余资源，你可以删除用于 TiDB 集群的命名空间。

{{< copyable "shell-regular" >}}

```shell
kubectl delete namespace tidb-cluster
```

### 销毁 Kubernetes 集群

销毁 Kubernetes 集群的方法取决于其创建方式。以下是销毁 Kubernetes 集群的步骤。

<SimpleTab>
<div label="kind">

如果使用了 kind 创建 Kubernetes 集群，在测试完成后，执行下面命令来销毁集群：

{{< copyable "shell-regular" >}}

``` shell
kind delete cluster
```

</div>

<div label="minikube">

如果使用了 minikube 创建 Kubernetes 集群，测试完成后，执行下面命令来销毁集群：

{{< copyable "shell-regular" >}}

``` shell
minikube delete
```

</div>
</SimpleTab>

## 探索更多

如果你想在生产环境部署，请参考以下文档：

在公有云上部署：

- [在 AWS EKS 上部署 TiDB 集群](deploy-on-aws-eks.md)
- [在 GCP GKE 上部署 TiDB 集群](deploy-on-gcp-gke.md)
- [在 Azure AKS 上部署 TiDB 集群](deploy-on-azure-aks.md)
- [在阿里云 ACK 上部署 TiDB 集群](deploy-on-alibaba-cloud.md)

自托管 Kubernetes 集群：

- [集群环境要求](prerequisites.md)
- 参考[本地 PV 配置](configure-storage-class.md#本地-pv-配置)让 TiKV 使用高性能本地存储
- [在 Kubernetes 部署 TiDB Operator](deploy-tidb-operator.md)
- [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)
