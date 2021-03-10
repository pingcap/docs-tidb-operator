---
title: 在标准 Kubernetes 上部署 TiDB 集群
summary: 介绍如何在标准 Kubernetes 集群上通过 TiDB Operator 部署 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/v1.0/deploy-on-general-kubernetes/','/docs-cn/dev/tidb-in-kubernetes/deploy/general-kubernetes/','/docs-cn/v3.1/tidb-in-kubernetes/deploy/general-kubernetes/','/docs-cn/v3.0/tidb-in-kubernetes/deploy/general-kubernetes/']
---

# 在标准 Kubernetes 上部署 TiDB 集群

本文主要描述了如何在标准的 Kubernetes 集群上通过 TiDB Operator 部署 TiDB 集群。

## 前置条件

* 参考 [TiDB Operator](deploy-tidb-operator.md) 完成集群中的 TiDB Operator 部署；
* 参考 [使用 Helm](tidb-toolkit.md#使用-helm) 安装 Helm 并配置 PingCAP 官方 chart 仓库。

## 配置 TiDB 集群

通过下面命令获取待安装的 tidb-cluster chart 的 `values.yaml` 配置文件：

{{< copyable "shell-regular" >}}

```shell
mkdir -p /home/tidb/<release-name> && \
helm inspect values pingcap/tidb-cluster --version=<chart-version> > /home/tidb/<release-name>/values-<release-name>.yaml
```

> **注意：**
>
> - `/home/tidb` 可以替换为你想用的目录。
> - `release-name` 将会作为 Kubernetes 相关资源（例如 Pod，Service 等）的前缀名，可以起一个方便记忆的名字，要求全局唯一，通过 `helm ls -q` 可以查看集群中已经有的 `release-name`。
> - `chart-version` 是 tidb-cluster chart 发布的版本，可以通过 `helm search -l tidb-cluster` 查看当前支持的版本。
> - 下文会用 `values.yaml` 指代 `/home/tidb/<release-name>/values-<release-name>.yaml`。

### 存储类型

集群默认使用 `local-storage` 存储类型。

- 生产环境：推荐使用本地存储，但实际 Kubernetes 集群中本地存储可能按磁盘类型进行了分类，例如 `nvme-disks`，`sas-disks`。
- 演示环境或功能性验证：可以使用网络存储，例如 `ebs`，`nfs` 等。

另外 TiDB 集群不同组件对磁盘的要求不一样，所以部署集群前要根据当前 Kubernetes 集群支持的存储类型以及使用场景为 TiDB 集群各组件选择合适的存储类型，通过修改 `values.yaml` 中各组件的 `storageClassName` 字段设置存储类型。关于 Kubernetes 集群支持哪些[存储类型](configure-storage-class.md)，请联系系统管理员确定。

> **注意：**
>
> 如果创建集群时设置了集群中不存在的存储类型，则会导致集群创建处于 Pending 状态，需要[将集群彻底销毁掉](destroy-a-tidb-cluster.md)。

### 集群拓扑

默认部署的集群拓扑是：3 个 PD Pod，3 个 TiKV Pod，2 个 TiDB Pod 和 1 个监控 Pod。在该部署拓扑下根据数据高可用原则，TiDB Operator 扩展调度器要求 Kubernetes 集群中至少有 3 个节点。如果 Kubernetes 集群节点个数少于 3 个，将会导致有一个 PD Pod 处于 Pending 状态，而 TiKV 和 TiDB Pod 也都不会被创建。

Kubernetes 集群节点个数少于 3 个时，为了使 TiDB 集群能启动起来，可以将默认部署的 PD 和 TiKV Pod 个数都减小到 1 个，或者将 `values.yaml` 中 `schedulerName` 改为 Kubernetes 内置调度器 `default-scheduler`。

> **警告：**
>
> `default-scheduler` 仅适用于演示环境，改为 `default-scheduler` 后，TiDB 集群的调度将无法保证数据高可用，另外一些其它特性也无法支持，例如 [TiDB Pod StableScheduling](https://github.com/pingcap/tidb-operator/blob/master/docs/design-proposals/tidb-stable-scheduling.md) 等。

其它更多配置参数请参考 [TiDB 集群部署配置文档](configure-a-tidb-cluster.md)。

## 部署 TiDB 集群

<<<<<<< HEAD
TiDB Operator 部署并配置完成后，可以通过下面命令部署 TiDB 集群：

{{< copyable "shell-regular" >}}

``` shell
helm install pingcap/tidb-cluster --name=<release-name> --namespace=<namespace> --version=<chart-version> -f /home/tidb/<release-name>/values-<release-name>.yaml
```
=======
在部署 TiDB 集群之前，需要先配置 TiDB 集群。请参阅[在 Kubernetes 中配置 TiDB 集群](configure-a-tidb-cluster.md)。

配置 TiDB 集群后，请按照以下步骤部署 TiDB 集群：

1. 创建 `Namespace`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace ${namespace}
    ```

    > **注意：**
    >
    > `namespace` 是[命名空间](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)，可以起一个方便记忆的名字，比如和 `cluster_name` 相同的名称。

2. 部署 TiDB 集群：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl apply -f ${cluster_name} -n ${namespace}
    ```

    > **注意：**
    >
    > 建议在 `cluster_name` 目录下组织 TiDB 集群的配置，并将其另存为 `${cluster_name}/tidb-cluster.yaml`。默认条件下，修改配置不会自动应用到 TiDB 集群中，只有在 Pod 重启时，才会重新加载新的配置文件。

    如果服务器没有外网，需要在有外网的机器上将 TiDB 集群用到的 Docker 镜像下载下来并上传到服务器上，然后使用 `docker load` 将 Docker 镜像安装到服务器上。

    部署一套 TiDB 集群会用到下面这些 Docker 镜像（假设 TiDB 集群的版本是 v4.0.10）：

    ```shell
    pingcap/pd:v4.0.10
    pingcap/tikv:v4.0.10
    pingcap/tidb:v4.0.10
    pingcap/tidb-binlog:v4.0.10
    pingcap/ticdc:v4.0.10
    pingcap/tiflash:v4.0.10
    pingcap/tidb-monitor-reloader:v1.0.1
    pingcap/tidb-monitor-initializer:v4.0.10
    grafana/grafana:6.0.1
    prom/prometheus:v2.18.1
    busybox:1.26.2
    ```

    接下来通过下面的命令将所有这些镜像下载下来：

    {{< copyable "shell-regular" >}}

    ```shell
    docker pull pingcap/pd:v4.0.10
    docker pull pingcap/tikv:v4.0.10
    docker pull pingcap/tidb:v4.0.10
    docker pull pingcap/tidb-binlog:v4.0.10
    docker pull pingcap/ticdc:v4.0.10
    docker pull pingcap/tiflash:v4.0.10
    docker pull pingcap/tidb-monitor-reloader:v1.0.1
    docker pull pingcap/tidb-monitor-initializer:v4.0.10
    docker pull grafana/grafana:6.0.1
    docker pull prom/prometheus:v2.18.1
    docker pull busybox:1.26.2

    docker save -o pd-v4.0.10.tar pingcap/pd:v4.0.10
    docker save -o tikv-v4.0.10.tar pingcap/tikv:v4.0.10
    docker save -o tidb-v4.0.10.tar pingcap/tidb:v4.0.10
    docker save -o tidb-binlog-v4.0.10.tar pingcap/tidb-binlog:v4.0.10
    docker save -o ticdc-v4.0.10.tar pingcap/ticdc:v4.0.10
    docker save -o tiflash-v4.0.10.tar pingcap/tiflash:v4.0.10
    docker save -o tidb-monitor-reloader-v1.0.1.tar pingcap/tidb-monitor-reloader:v1.0.1
    docker save -o tidb-monitor-initializer-v4.0.10.tar pingcap/tidb-monitor-initializer:v4.0.10
    docker save -o grafana-6.0.1.tar grafana/grafana:6.0.1
    docker save -o prometheus-v2.18.1.tar prom/prometheus:v2.18.1
    docker save -o busybox-1.26.2.tar busybox:1.26.2
    ```

    接下来将这些 Docker 镜像上传到服务器上，并执行 `docker load` 将这些 Docker 镜像安装到服务器上：

    {{< copyable "shell-regular" >}}

    ```shell
    docker load -i pd-v4.0.10.tar
    docker load -i tikv-v4.0.10.tar
    docker load -i tidb-v4.0.10.tar
    docker load -i tidb-binlog-v4.0.10.tar
    docker load -i ticdc-v4.0.10.tar
    docker load -i tiflash-v4.0.10.tar
    docker load -i tidb-monitor-reloader-v1.0.1.tar
    docker load -i tidb-monitor-initializer-v4.0.10.tar
    docker load -i grafana-6.0.1.tar
    docker load -i prometheus-v2.18.1.tar
    docker load -i busybox-1.26.2.tar
    ```

3. 通过下面命令查看 Pod 状态：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl get po -n ${namespace} -l app.kubernetes.io/instance=${cluster_name}
    ```

单个 Kubernetes 集群中可以利用 TiDB Operator 部署管理多套 TiDB 集群，重复以上步骤并将 `cluster_name` 替换成不同名字即可。不同集群既可以在相同 `namespace` 中，也可以在不同 `namespace` 中，可根据实际需求进行选择。

## 初始化 TiDB 集群

如果要在部署完 TiDB 集群后做一些初始化工作，参考 [Kubernetes 上的集群初始化配置](initialize-a-cluster.md)进行配置。
>>>>>>> be6821b... CI: add file format lint script to check manual line breaks and file encoding (#1126)

> **注意：**
>
> `namespace` 是[命名空间](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)，你可以起一个方便记忆的名字，比如和 `release-name` 相同的名称。

通过下面命令可以查看 Pod 状态：

{{< copyable "shell-regular" >}}

``` shell
kubectl get po -n <namespace> -l app.kubernetes.io/instance=<release-name>
```

单个 Kubernetes 集群中可以利用 TiDB Operator 部署管理多套 TiDB 集群，重复以上命令并将 `release-name` 替换成不同名字即可。不同集群既可以在相同 `namespace` 中，也可以在不同 `namespace` 中，可根据实际需求进行选择。
