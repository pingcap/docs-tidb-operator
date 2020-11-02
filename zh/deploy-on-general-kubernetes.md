---
title: 在标准 Kubernetes 上部署 TiDB 集群
summary: 介绍如何在标准 Kubernetes 集群上通过 TiDB Operator 部署 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-on-general-kubernetes/']
---

# 在标准 Kubernetes 上部署 TiDB 集群

本文主要描述了如何在标准的 Kubernetes 集群上通过 TiDB Operator 部署 TiDB 集群。

## 前置条件

* TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 部署 TiDB 集群

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

    部署一套 TiDB 集群会用到下面这些 Docker 镜像（假设 TiDB 集群的版本是 v4.0.7）：

    ```shell
    pingcap/pd:v4.0.7
    pingcap/tikv:v4.0.7
    pingcap/tidb:v4.0.7
    pingcap/tidb-binlog:v4.0.7
    pingcap/ticdc:v4.0.7
    pingcap/tiflash:v4.0.7
    pingcap/tidb-monitor-reloader:v1.0.1
    pingcap/tidb-monitor-initializer:v4.0.7
    grafana/grafana:6.0.1
    prom/prometheus:v2.18.1
    busybox:1.26.2
    ```

    接下来通过下面的命令将所有这些镜像下载下来：

    {{< copyable "shell-regular" >}}

    ```shell
    docker pull pingcap/pd:v4.0.7
    docker pull pingcap/tikv:v4.0.7
    docker pull pingcap/tidb:v4.0.7
    docker pull pingcap/tidb-binlog:v4.0.7
    docker pull pingcap/ticdc:v4.0.7
    docker pull pingcap/tiflash:v4.0.7
    docker pull pingcap/tidb-monitor-reloader:v1.0.1
    docker pull pingcap/tidb-monitor-initializer:v4.0.7
    docker pull grafana/grafana:6.0.1
    docker pull prom/prometheus:v2.18.1
    docker pull busybox:1.26.2

    docker save -o pd-v4.0.7.tar pingcap/pd:v4.0.7
    docker save -o tikv-v4.0.7.tar pingcap/tikv:v4.0.7
    docker save -o tidb-v4.0.7.tar pingcap/tidb:v4.0.7
    docker save -o tidb-binlog-v4.0.7.tar pingcap/tidb-binlog:v4.0.7
    docker save -o ticdc-v4.0.7.tar pingcap/ticdc:v4.0.7
    docker save -o tiflash-v4.0.7.tar pingcap/tiflash:v4.0.7
    docker save -o tidb-monitor-reloader-v1.0.1.tar pingcap/tidb-monitor-reloader:v1.0.1
    docker save -o tidb-monitor-initializer-v4.0.7.tar pingcap/tidb-monitor-initializer:v4.0.7
    docker save -o grafana-6.0.1.tar grafana/grafana:6.0.1
    docker save -o prometheus-v2.18.1.tar prom/prometheus:v2.18.1
    docker save -o busybox-1.26.2.tar busybox:1.26.2
    ```

    接下来将这些 Docker 镜像上传到服务器上，并执行 `docker load` 将这些 Docker 镜像安装到服务器上：

    {{< copyable "shell-regular" >}}

    ```shell
    docker load -i pd-v4.0.7.tar
    docker load -i tikv-v4.0.7.tar
    docker load -i tidb-v4.0.7.tar
    docker load -i tidb-binlog-v4.0.7.tar
    docker load -i ticdc-v4.0.7.tar
    docker load -i tiflash-v4.0.7.tar
    docker load -i tidb-monitor-reloader-v1.0.1.tar
    docker load -i tidb-monitor-initializer-v4.0.7.tar
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

> **注意：**
>
> TiDB（v4.0.2 起）默认会定期收集使用情况信息，并将这些信息分享给 PingCAP 用于改善产品。若要了解所收集的信息详情及如何禁用该行为，请参见[遥测](https://docs.pingcap.com/zh/tidb/stable/telemetry)。
