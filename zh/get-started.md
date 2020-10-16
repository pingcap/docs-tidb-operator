---
title: Kubernetes 上使用 TiDB Operator 快速上手
summary: 介绍如何在 Kubernetes 上使用 TiDB Operator 部署 TiDB 集群
aliases: ['/docs-cn/tidb-in-kubernetes/dev/get-started/','/docs-cn/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-dind/', '/docs-cn/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-kind/', '/docs-cn/dev/tidb-in-kubernetes/deploy-tidb-from-kubernetes-minikube/','/docs-cn/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind/','/docs-cn/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube/','/zh/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-kind/','/zh/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-gke/','/zh/tidb-in-kubernetes/dev/deploy-tidb-from-kubernetes-minikube']
---

# Kubernetes 上使用 TiDB Operator 快速上手

本文档介绍了如何创建一个简单的 Kubernetes 集群，部署 TiDB Operator，并使用 TiDB Operator 部署 TiDB 集群。

> **警告：**
> 
> 本文中部署例子仅用于测试目的。**不要**直接用于生产环境。

基本步骤如下：

1. [创建 Kubernetes 集群](#创建-kubernetes-集群)
2. [部署 TiDB Operator](#部署-tidb-operator)
3. [部署 TiDB Cluster](#部署-tidb-集群)
4. [连接 TiDB](#连接-tidb)

如果你已经有一个 Kubernetes 集群，可直接[部署 TiDB Operator](#部署-tidb-operator)。

如果你想做生产部署，参考以下文档：

- 公有云
    - [AWS 部署文档](deploy-on-aws-eks.md)
    - [GKE 部署文档 (beta)](deploy-on-gcp-gke.md)
    - [阿里云部署文档](deploy-on-alibaba-cloud.md)
- 其他 Kubernetes 集群
    - 熟悉[集群环境要求](prerequisites.md)
    - 参考[本地 PV 配置](configure-storage-class.md#本地-pv-配置) 配置本地存储，以便让 TiKV 使用低延迟本地存储
    - 参考[在 Kubernetes 部署 TiDB Operator](deploy-tidb-operator.md) 部署 TiDB Operator 
    - 参考[在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md) 部署 TiDB 集群

## 创建 Kubernetes 集群

本节介绍了两种创建简单 Kubernetes 集群的方法，可用于测试在 TiDB Operator 下运行的 TiDB 集群。选择最适合你的环境的方案。

- [使用 kind](#使用-kind-创建-kubernetes-集群) (在 Docker 中运行 Kubernetes)
- [使用 minikube](#使用-minikube-创建-kubernetes-集群) (在虚拟机中运行 Kubernetes)

你也可以使用 Google Cloud Shell 在 Google Cloud Platform 的 Google Kubernetes Engine 中部署 Kubernetes 集群，并遵循教程来部署 TiDB Operator 和 TiDB 集群：

- [打开 Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=zh/deploy-tidb-from-kubernetes-gke.md)

### 使用 kind 创建 Kubernetes 集群

本节介绍如何使用 kind 部署 Kubernetes 集群。

[kind](https://kind.sigs.k8s.io/) 是用于使用 Docker 容器作为集群节点运行本地 Kubernetes 集群的工具。它是为测试本地 Kubernetes 集群而开发的。Kubernetes 集群版本取决于 kind 使用的节点镜像，你可以指定要用于节点的镜像并选择任何发布的版本。请参阅 [Docker hub](https://hub.docker.com/r/kindest/node/tags) 以查看可用 tags。默认使用当前 kind 支持的最新版本。

> **警告：**
> 
> 仅用于测试目的。**不要**直接用于生产环境。

部署前，请确保满足以下要求：

- [docker](https://docs.docker.com/install/)：版本 >= 17.03
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl)：版本 >= 1.12
- [kind](https://kind.sigs.k8s.io/)：版本 >= 0.8.0
- 若使用 Linux, [net.ipv4.ip_forward](https://linuxconfig.org/how-to-turn-on-off-ip-forwarding-in-linux) 需要被设置为 `1`

以下以 0.8.1 版本为例：

{{< copyable "shell-regular" >}}

```shell
kind create cluster
```

期望输出：

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

检查集群是否创建成功：

{{< copyable "shell-regular" >}}

```shell
kubectl cluster-info
```

期望输出：

```
Kubernetes master is running at https://127.0.0.1:51026
KubeDNS is running at https://127.0.0.1:51026/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

现在就可以开始[部署 TiDB Operator](#部署-tidb-operator)！

测试完成后，销毁集群，执行下面命令：

{{< copyable "shell-regular" >}}

``` shell
kind delete cluster
```

### 使用 minikube 创建 Kubernetes 集群

本节介绍如何使用 minikube 部署 Kubernetes 集群。

[Minikube](https://kubernetes.io/docs/setup/minikube/) 可以在虚拟机中创建一个 Kubernetes 集群，可在 macOS, Linux 和 Windows 上运行。

> **警告：**
> 
> 仅用于测试目的。**不要**直接用于生产环境。

部署前，请确保满足以下要求：

- [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)：版本 1.0.0+
    - Minikube 需要安装一个兼容的 hypervisor，详情见官方安装教程。
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl): 版本 >= 1.12

> **注意：**
>
> - 尽管 Minikube 支持通过 `--vm-driver=none` 选项使用主机 Docker 而不使用虚拟机，但是目前尚没有针对 TiDB Operator 做过全面的测试，可能会无法正常工作。如果你想在不支持虚拟化的系统（例如，VPS）上试用 TiDB Operator，可以考虑使用 [kind](get-started.md#使用-kind-创建-kubernetes-集群)。

安装完 Minikube 后，可以执行下面命令启动一个 Kubernetes 集群：

{{< copyable "shell-regular" >}}

```shell
minikube start
```

一切运行正常，会看到类似下面的输出。根据操作系统和使用的 hypervisor 会有些许差异。

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

对于中国大陆用户，可以使用国内 gcr.io mirror 仓库，例如 `registry.cn-hangzhou.aliyuncs.com/google_containers`。

{{< copyable "shell-regular" >}}

``` shell
minikube start --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers
```

或者给 Docker 配置 HTTP/HTTPS 代理。

将下面命令中的 `127.0.0.1:1086` 替换为你自己的 HTTP/HTTPS 代理地址：

{{< copyable "shell-regular" >}}

``` shell
minikube start --docker-env https_proxy=http://127.0.0.1:1086 \
  --docker-env http_proxy=http://127.0.0.1:1086
```

> **注意：**
>
> 由于 Minikube（默认）通过虚拟机运行，`127.0.0.1` 是虚拟机本身，因此，有些情况下可能需要将其修改为你的主机的实际 IP。

参考 [Minikube setup](https://kubernetes.io/docs/setup/minikube/) 查看配置虚拟机和 Kubernetes 集群的更多选项。

执行以下命令检查集群状态，并确保可以通过 `kubectl` 访问集群:

{{< copyable "shell-regular" >}}

```
kubectl cluster-info
```

期望输出：

```
Kubernetes master is running at https://192.168.64.2:8443
KubeDNS is running at https://192.168.64.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

现在就可以开始[部署 TiDB Operator](#部署-tidb-operator)！

测试完成后，销毁集群，执行下面命令：

{{< copyable "shell-regular" >}}

``` shell
minikube delete
```

## 部署 TiDB Operator

开始之前，确保以下要求已满足：

- 可以使用 `kubectl` 访问的 Kubernetes 集群
- [Helm](https://helm.sh/docs/intro/install/): Helm 2 (>= Helm 2.16.5) 或者最新的 Helm 3 稳定版

1. 安装 TiDB Operator CRDs

    TiDB Operator 包含许多实现 TiDB 集群不同组件的自定义资源类型 (CRD)。执行以下命令安装 CRD 到集群中：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.1.6/manifests/crd.yaml
    ```

    期望输出：

    ```
    customresourcedefinition.apiextensions.k8s.io/tidbclusters.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/backups.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/restores.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/backupschedules.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbmonitors.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbinitializers.pingcap.com created
    customresourcedefinition.apiextensions.k8s.io/tidbclusterautoscalers.pingcap.com created
    ```

2. 安装 TiDB Operator

    TiDB Operator 使用 helm 安装，使用用法略有不同，取决于 Helm 版本是 2 还是 3 。可使用 `helm version --short` 命令查看安装的版本：

    1. 如果使用的是 Helm 2，你需要安装服务端组件 tiller 。若使用 Helm 3 可跳过此步。 

        应用 tiller 组件 RBAC 规则并安装 tiller 。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/tiller-rbac.yaml && \
        helm init --service-account=tiller --upgrade
        ```

        执行以下命令，检查并确认 tiller 的 Pod 是否运行起来：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get po -n kube-system -l name=tiller
        ```

        期望输出：

        ```
        NAME                            READY   STATUS    RESTARTS   AGE
        tiller-deploy-b7b9488b5-j6m6p   1/1     Running   0          18s
        ```

        当 Ready 栏显示 `1/1` 时表明已经运行起来，可进入下一步操作。

    2. 添加 PingCAP 仓库

        {{< copyable "shell-regular" >}}

        ```shell
        helm repo add pingcap https://charts.pingcap.org/
        ```

        期望输出：

        ```
        "pingcap" has been added to your repositories  
        ```

     3. 为 TiDB Operator 创建一个命名空间

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create namespace tidb-admin
        ```

        期望输出：

        ```
        namespace/tidb-admin created
        ```

     4. 安装 TiDB Operator

        `helm install` 语法在 Helm 2 和 Helm 3 下略有不同。  
        
        - Helm 2:

            {{< copyable "shell-regular" >}}

            ```shell
            helm install --namespace tidb-admin --name tidb-operator pingcap/tidb-operator --version v1.1.6
            ```

            如果访问 Docker Hub 网速较慢，可以使用阿里云上的镜像：

            {{< copyable "shell-regular" >}}

            ```
            helm install --namespace tidb-admin --name tidb-operator pingcap/tidb-operator --version v1.1.6 \
              --set operatorImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-operator:v1.1.6 \
              --set tidbBackupManagerImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-backup-manager:v1.1.6 \
              --set scheduler.kubeSchedulerImageName=registry.cn-hangzhou.aliyuncs.com/google_containers/kube-scheduler
            ```

            期望输出：

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
            Make sure tidb-operator components are running:

                kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
            ```  

        - Helm 3:

            {{< copyable "shell-regular" >}}

            ```shell
            helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.1.6
            ```

            如果访问 Docker Hub 网速较慢，可以使用阿里云上的镜像：

            {{< copyable "shell-regular" >}}

            ```
            helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.1.6 \
              --set operatorImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-operator:v1.1.6 \
              --set tidbBackupManagerImage=registry.cn-beijing.aliyuncs.com/tidb/tidb-backup-manager:v1.1.6 \
              --set scheduler.kubeSchedulerImageName=registry.cn-hangzhou.aliyuncs.com/google_containers/kube-scheduler
            ```

            期望输出：

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

        使用以下命令检查 TiDB Operator 组件是否运行起来：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
        ```

        期望输出：

        ```
        NAME                                       READY   STATUS    RESTARTS   AGE
        tidb-controller-manager-6d8d5c6d64-b8lv4   1/1     Running   0          2m22s
        tidb-scheduler-644d59b46f-4f6sb            2/2     Running   0          2m22s
        ```

        当所有的 pods 都处于 Running 状态时，可进行下一步操作。
    
## 部署 TiDB 集群

1. 部署 TiDB 集群

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl create namespace tidb-cluster && \
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-cluster.yaml && \
    kubectl -n tidb-cluster apply -f tidb-cluster.yaml
    ```

    如果访问 Docker Hub 网速较慢，可以使用阿里云上的镜像：

    {{< copyable "shell-regular" >}}

    ```
    kubectl create namespace tidb-cluster && \
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic-cn/tidb-cluster.yaml && \
    kubectl -n tidb-cluster apply -f tidb-cluster.yaml
    ```

    期望输出：

    ```
    namespace/tidb-cluster created
    tidbcluster.pingcap.com/basic created
    ```

2. 部署 TiDB 集群监控

    {{< copyable "shell-regular" >}}

    ``` shell
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic/tidb-monitor.yaml && \
    kubectl -n tidb-cluster apply -f tidb-monitor.yaml
    ```

    如果访问 Docker Hub 网速较慢，可以使用阿里云上的镜像：

    {{< copyable "shell-regular" >}}

    ```
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/basic-cn/tidb-monitor.yaml && \
    kubectl -n tidb-cluster apply -f tidb-monitor.yaml
    ```

    期望输出：

    ```
    tidbmonitor.pingcap.com/basic created
    ```

3. 查看 Pod 状态

    {{< copyable "shell-regular" >}}

    ``` shell
    watch kubectl get po -n tidb-cluster
    ```

    期望输出：

    ```
    NAME                              READY   STATUS            RESTARTS   AGE
    basic-discovery-6bb656bfd-kjkxw   1/1     Running           0          29s
    basic-monitor-5fc8589c89-2mwx5    0/3     PodInitializing   0          20s
    basic-pd-0                        1/1     Running           0          29s
    ```

    等待所有组件 pods 都启动，看到每种类型（`-pd`，`-tikv` 和 `-tidb`）都处于 Running 状态时，您可以按 Ctrl-C 返回命令行，然后进行下一步：[连接到 TiDB 集群](#连接-tidb)。

    期望输出：

    ```
    NAME                              READY   STATUS    RESTARTS   AGE
    basic-discovery-6bb656bfd-xl5pb   1/1     Running   0          9m9s
    basic-monitor-5fc8589c89-gvgjj    3/3     Running   0          8m58s
    basic-pd-0                        1/1     Running   0          9m8s
    basic-tidb-0                      2/2     Running   0          7m14s
    basic-tikv-0                      1/1     Running   0          8m13s
    ```

## 连接 TiDB

1. 安装 `mysql` 命令行工具

    要连接到 TiDB，您需要在使用 `kubectl` 的主机上安装与 MySQL 兼容的命令行客户端。可以安装 MySQL Server，MariaDB Server，Percona Server 的 mysql 可执行文件，也可以从操作系统软件仓库中安装。

2. 转发 4000 端口

    首先，将端口从本地主机转发到 Kubernetes 中的 TiDB **Servcie**。 我们先获取 tidb-cluster 命名空间中的服务列表：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl get svc -n tidb-cluster
    ```

    期望输出：

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

    这个例子中，TiDB **Service** 是 **basic-tidb** 。使用以下命令转发本地端口到集群：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl port-forward -n tidb-cluster svc/basic-tidb 4000 > pf4000.out &
    ```

    命令会运行在后台，并将输出转发到文件 `pf4000.out` 。所以我们可以继续在当前 shell 会话中继续执行命令。

3. 连接 TiDB

    > **注意：**
    >
    > + 当使用 MySQL Client 8.0 访问 TiDB 服务（TiDB 版本 < v4.0.7）时，如果用户账户有配置密码，必须显示指定 `--default-auth=mysql_native_password` 参数，因为 `mysql_native_password` [不再是默认的插件](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password)。

    {{< copyable "shell-regular" >}}

    ``` shell
    mysql -h 127.0.0.1 -P 4000 -u root
    ```

    期望输出：

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

    以下是一些可以用来验证集群功能的命令：

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

    ```
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

4. 载入 Grafana 面板

    像上面对 TiDB 4000 端口转发一样，可以转发 Grafana 端口，以便本地访问 Grafana 面板。

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl port-forward -n tidb-cluster svc/basic-grafana 3000 > pf3000.out &
    ```

    Grafana 面板可在 kubectl 所运行的主机上通过 <http://localhost:3000> 访问。注意，如果你是非本机（比如 Docker 容器或远程服务器）上运行 `kubectl port-forward`，将无法在本地浏览器里通过 `localhost:3000` 访问。

    默认用户名和密码都是 "admin" 。

    了解更多使用 TiDB Operator 部署 TiDB 集群监控的信息，可以查阅[使用 TidbMonitor 监控 TiDB 集群](monitor-using-tidbmonitor.md)。

## 升级 TiDB 集群

TiDB Operator 还可简化 TiDB 集群的滚动升级。以下示例更新 TiDB 版本到 "nightly" 版本。

Kubernetes 可以直接编辑已部署的资源，或给已部署的资源应用补丁。

`kubectl edit` 在交互式文本编辑器中打开资源，管理员可以在其中进行更改并保存。如果更改有效，它们将被提交到集群。如果更改无效，它们将会被拒绝并显示一条错误消息。请注意，目前尚不对所有字段进行验证。保存某些更改后，即使更改被接受也不一定会对集群生效。

`kubectl patch` 可直接应用补丁。Kubernetes 支持几种不同的补丁策略，每种策略有不同的功能、格式等。可参考 [Kubernetes Patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) 了解更多细节。

1. 修改 TiDB 集群版本

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc basic -n tidb-cluster --type merge -p '{"spec": {"version": "release-4.0-nightly"} }'
    ```

    期望输出：

    ```
    tidbcluster.pingcap.com/basic patched
    ```  

2. 等待所有 pods 重启

    执行此命令以了解集群升级组件时的进度。你可以看到某些 pods 进入 Terminating 状态后，又回到 ContainerCreating，最后重新进入 Running 状态。

    {{< copyable "shell-regular" >}}

    ```
    watch kubectl get po -n tidb-cluster
    ```

    期望输出：

    ```
    NAME                              READY   STATUS        RESTARTS   AGE
    basic-discovery-6bb656bfd-7lbhx   1/1     Running       0          24m
    basic-pd-0                        1/1     Terminating   0          5m31s
    basic-tidb-0                      2/2     Running       0          2m19s
    basic-tikv-0                      1/1     Running       0          4m13s
    ```

3. 转发端口

    当所有 pods 都重启后，将看到版本号已更改。现在可以重新运行 `kubeclt port-forward` 命令进行端口转发，以便访问集群中 TiDB 集群。

    {{< copyable "shell-regular" >}}

    ```
    kubectl port-forward -n tidb-cluster svc/basic-tidb 4000 > pf4000.out &
    ```

4. 访问并检查集群版本

    {{< copyable "shell-regular" >}}

    ```
    mysql -h 127.0.0.1 -P 4000 -u root -e 'select tidb_version()\G'
    ```

    期望输出：

    > **注意：**
    > `release-4.0-nightly` 不是固定版本，不同时间会有不同结果

    ```
    *************************** 1. row ***************************
    tidb_version(): Release Version: v4.0.0-6-gdec49a126
    Edition: Community
    Git Commit Hash: dec49a12654c4f09f6fedfd2a0fb0154fc095449
    Git Branch: release-4.0
    UTC Build Time: 2020-06-01 10:07:32
    GoVersion: go1.13
    Race Enabled: false
    TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
    Check Table Before Drop: false
    ```

## 销毁 TiDB 集群

完成测试后，您可能希望销毁 TiDB 集群：

销毁 Kubernetes 集群取决于 Kubernetes 集群的创建方式。可参考前面 Kubernetes 创建文档部分。以下是销毁 TiDB 集群方式，不会影响 Kubernetes 集群本身。

1. 删除 TiDB Cluster

    {{< copyable "shell-regular" >}}

     ```shell
    kubectl delete tc basic -n tidb-cluster
    ```

2. 删除 TiDB Monitor

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete tidbmonitor basic -n tidb-cluster
    ```

3. 删除 PV 数据

    如果您的部署具有持久性数据存储，则删除 TiDB 群集将不会删除群集的数据。 如果不再需要数据，可以运行以下命令来清理数据：

     {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pvc -n tidb-cluster -l app.kubernetes.io/instance=basic,app.kubernetes.io/managed-by=tidb-operator && \
    kubectl get pv -l app.kubernetes.io/namespace=tidb-cluster,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=basic -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
    ```   

4. 删除命名空间

    为确保没有残余资源，您可以删除用于 TiDB 集群的命名空间。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete namespace tidb-cluster
    ```  

5. 停止 `kubectl` 的端口转发

    如果您仍在运行正在转发端口的 `kubectl` 进程，请终止它们：

    {{< copyable "shell-regular" >}}

    ```shell
    pgrep -lfa kubectl
    ```

查看更多相关信息，可以查阅[销毁 TiDB 集群](#销毁-tidb-集群)。
