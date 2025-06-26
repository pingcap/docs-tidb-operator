---
title: 暂停同步 Kubernetes 上的 TiDB 集群
summary: 介绍如何暂停同步 Kubernetes 上的 TiDB 集群。
---

# 暂停同步 Kubernetes 上的 TiDB 集群

本文介绍如何通过配置暂停同步 Kubernetes 上的 TiDB 集群。

## TiDB Operator 的同步机制

在 TiDB Operator 中，控制器会不断对比 Custom Resource (CR) 对象中记录的期望状态与实际状态，并通过创建、更新或删除 Kubernetes 资源来驱动 TiDB 集群满足期望状态。这个不断调整的过程通常被称为**同步**。更多细节参见 [TiDB Operator 架构](architecture.md)。

## 暂停同步的应用场景

暂停同步适用于以下场景：

- 避免意外的滚动升级

    为防止 TiDB Operator 新版本的兼容性问题影响集群，升级 TiDB Operator 之前，可以先暂停同步集群。升级 TiDB Operator 之后，逐个恢复同步集群或者在指定时间恢复同步集群，以此来观察 TiDB Operator 版本升级对集群的影响。

- 避免多次滚动重启集群

    在某些情况下，一段时间内可能会多次修改 TiDB 集群配置，但是又不想多次滚动重启集群。为了避免多次滚动重启集群，可以先暂停同步集群，在此期间，对 TiDB 集群的任何配置都不会生效。集群配置修改完成后，恢复集群同步，此时暂停同步期间的所有配置修改都能在一次重启过程中被应用。

- 维护时间窗口

    在某些情况下，只允许在特定时间窗口内滚动升级或重启 TiDB 集群。因此可以在维护时间窗口之外的时间段暂停 TiDB 集群的同步过程，这样在维护时间窗口之外对 TiDB 集群的任何配置都不会生效；在维护时间窗口内，可以通过恢复 TiDB 集群同步来允许滚动升级或者重启 TiDB 集群。

## 暂停同步 TiDB 集群

如果想要暂停同步 TiDB 集群，可以在 Cluster CR 中配置 `spec.paused: true`。

1. 使用以下命令修改集群配置，其中 `${cluster_name}` 表示 TiDB 集群名称，`${namespace}` 表示 TiDB 集群所在的 namespace。

    ```shell
    kubectl patch cluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"paused": true}}'
    ```

2. TiDB 集群同步暂停后，可以使用以下命令查看 TiDB Operator Pod 日志，确认 TiDB 集群同步状态。其中 `${pod_name}` 表示 TiDB Operator Pod 的名称，`${namespace}` 表示 TiDB Operator 所在的 namespace。

    ```shell
    kubectl logs ${pod_name} -n ${namespace} | grep paused
    ```

    输出类似如下内容时，表示 TiDB 集群同步已经暂停。

    ```
    2025-04-25T09:27:27.866Z    INFO    TiCDC    cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.866Z    INFO    TiDB     cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.867Z    INFO    TiFlash  cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.868Z    INFO    PD       cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.868Z    INFO    TiKV     cluster paused is updating    {"from": false, "to": true}
    ```

## 恢复同步 TiDB 集群

如果想要恢复 TiDB 集群的同步，可以在 Cluster CR 中配置 `spec.paused: false`。恢复同步后，TiDB Operator 会立即开始处理暂停期间累积的所有配置变更。

1. 使用以下命令修改集群配置，其中 `${cluster_name}` 表示 TiDB 集群名称，`${namespace}` 表示 TiDB 集群所在的 namespace。

    ```shell
    kubectl patch cluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"paused": false}}'
    ```

2. 恢复 TiDB 集群同步后，可以使用以下命令查看 TiDB Operator Pod 日志，确认 TiDB 集群同步状态。其中 `${pod_name}` 表示 TiDB Operator Pod 的名称，`${namespace}` 表示 TiDB Operator 所在的 namespace。

    ```shell
    kubectl logs ${pod_name} -n ${namespace} | grep "paused"
    ```

    输出结果示例如下，可以看到同步成功时间戳（`cluster paused` 状态从 `true` 变为 `false` 的时间戳）大于暂停同步日志中显示的时间戳（`cluster paused` 状态从 `false` 变为 `true` 的时间戳），表示 TiDB 集群同步已经被恢复。

    ```
    2025-04-25T09:32:38.867Z    INFO    TiKV     cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    PD       cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiFlash  cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiCDC    cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiDB     cluster paused is updating    {"from": true, "to": false}
    ```
